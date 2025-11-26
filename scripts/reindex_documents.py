"""
Script de réindexation automatique des documents
Détecte les nouveaux PDFs et met à jour ChromaDB
"""

import os
import sys
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import logging
import hashlib
import json
from datetime import datetime

# Ajouter le chemin parent pour imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.document_processor import DocumentProcessor

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentIndexer:
    """Gestion de l'indexation des documents"""
    
    def __init__(self, documents_dir: str = "./documents"):
        self.documents_dir = Path(documents_dir)
        self.metadata_file = Path(".dvc/document_metadata.json")
        self.doc_processor = DocumentProcessor(documents_dir)
        
        # ChromaDB
        self.chroma_client = chromadb.Client()
        try:
            self.collection = self.chroma_client.get_collection("documents")
            logger.info("✅ Collection ChromaDB chargée")
        except:
            self.collection = self.chroma_client.create_collection("documents")
            logger.info("✅ Nouvelle collection ChromaDB créée")
        
        # Modèle d'embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def get_file_hash(self, file_path: Path) -> str:
        """Calculer le hash MD5 d'un fichier"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def load_metadata(self) -> dict:
        """Charger les métadonnées des documents indexés"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_metadata(self, metadata: dict):
        """Sauvegarder les métadonnées"""
        self.metadata_file.parent.mkdir(exist_ok=True)
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def detect_changes(self) -> dict:
        """Détecter les documents nouveaux/modifiés/supprimés"""
        metadata = self.load_metadata()
        current_files = {f.name: self.get_file_hash(f) 
                        for f in self.documents_dir.glob("*.pdf")}
        
        changes = {
            "new": [],
            "modified": [],
            "deleted": [],
            "unchanged": []
        }
        
        # Nouveaux ou modifiés
        for filename, file_hash in current_files.items():
            if filename not in metadata:
                changes["new"].append(filename)
            elif metadata[filename]["hash"] != file_hash:
                changes["modified"].append(filename)
            else:
                changes["unchanged"].append(filename)
        
        # Supprimés
        for filename in metadata.keys():
            if filename not in current_files:
                changes["deleted"].append(filename)
        
        return changes, current_files
    
    def chunk_text(self, text: str, chunk_size: int = 1000) -> list:
        """Découper le texte en chunks"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_length += len(word) + 1
            if current_length > chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def remove_document_chunks(self, filename: str):
        """Supprimer tous les chunks d'un document de ChromaDB"""
        try:
            # Récupérer tous les IDs avec ce filename
            results = self.collection.get(
                where={"source": filename}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"🗑️  Supprimé {len(results['ids'])} chunks de {filename}")
        except Exception as e:
            logger.error(f"Erreur suppression {filename}: {e}")
    
    def index_document(self, filename: str):
        """Indexer un document dans ChromaDB"""
        file_path = self.documents_dir / filename
        
        # Extraire le texte
        text = self.doc_processor.extract_text_from_pdf(file_path)
        if not text:
            logger.warning(f"⚠️  Pas de texte extrait de {filename}")
            return 0
        
        # Découper en chunks
        chunks = self.chunk_text(text)
        logger.info(f"📄 {filename}: {len(chunks)} chunks créés")
        
        # Générer embeddings
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        # Préparer les données
        chunk_ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename} for _ in chunks]
        
        # Ajouter à ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=chunk_ids
        )
        
        return len(chunks)
    
    def reindex_all(self):
        """Réindexer tous les documents"""
        logger.info("🔄 Réindexation complète de tous les documents...")
        
        # Supprimer toute la collection
        self.chroma_client.delete_collection("documents")
        self.collection = self.chroma_client.create_collection("documents")
        logger.info("🗑️  Collection ChromaDB réinitialisée")
        
        # Indexer tous les PDFs
        pdf_files = list(self.documents_dir.glob("*.pdf"))
        total_chunks = 0
        metadata = {}
        
        for pdf_file in pdf_files:
            chunks = self.index_document(pdf_file.name)
            total_chunks += chunks
            
            metadata[pdf_file.name] = {
                "hash": self.get_file_hash(pdf_file),
                "chunks": chunks,
                "indexed_at": datetime.now().isoformat()
            }
        
        self.save_metadata(metadata)
        logger.info(f"✅ Réindexation terminée: {len(pdf_files)} documents, {total_chunks} chunks")
    
    def incremental_reindex(self):
        """Réindexation incrémentale (seulement les changements)"""
        logger.info("🔍 Détection des changements...")
        
        changes, current_files = self.detect_changes()
        
        # Afficher le résumé
        logger.info(f"""
📊 Changements détectés:
   - Nouveaux: {len(changes['new'])}
   - Modifiés: {len(changes['modified'])}
   - Supprimés: {len(changes['deleted'])}
   - Inchangés: {len(changes['unchanged'])}
        """)
        
        if not any([changes['new'], changes['modified'], changes['deleted']]):
            logger.info("✅ Aucun changement détecté")
            return
        
        metadata = self.load_metadata()
        
        # Traiter les suppressions
        for filename in changes['deleted']:
            self.remove_document_chunks(filename)
            del metadata[filename]
        
        # Traiter les modifications (supprimer puis réindexer)
        for filename in changes['modified']:
            logger.info(f"🔄 Mise à jour: {filename}")
            self.remove_document_chunks(filename)
            chunks = self.index_document(filename)
            metadata[filename] = {
                "hash": current_files[filename],
                "chunks": chunks,
                "indexed_at": datetime.now().isoformat()
            }
        
        # Traiter les nouveaux documents
        for filename in changes['new']:
            logger.info(f"➕ Nouveau document: {filename}")
            chunks = self.index_document(filename)
            metadata[filename] = {
                "hash": current_files[filename],
                "chunks": chunks,
                "indexed_at": datetime.now().isoformat()
            }
        
        self.save_metadata(metadata)
        logger.info("✅ Réindexation incrémentale terminée")


def main():
    """Point d'entrée du script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Réindexation des documents")
    parser.add_argument(
        "--mode",
        choices=["full", "incremental"],
        default="incremental",
        help="Mode de réindexation (full=tout, incremental=changements)"
    )
    parser.add_argument(
        "--documents-dir",
        default="./documents",
        help="Chemin vers le dossier documents"
    )
    
    args = parser.parse_args()
    
    indexer = DocumentIndexer(args.documents_dir)
    
    if args.mode == "full":
        indexer.reindex_all()
    else:
        indexer.incremental_reindex()


if __name__ == "__main__":
    main()
