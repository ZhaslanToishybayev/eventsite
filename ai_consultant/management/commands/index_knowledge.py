import os
from django.core.management.base import BaseCommand
from django.conf import settings
from ai_consultant.services.indexing import DocumentIndexer

class Command(BaseCommand):
    help = 'Index knowledge base documents and club data for the AI Agent'

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Starting knowledge base indexing...")
        
        indexer = DocumentIndexer()
        
        # 1. Index Help Docs
        docs_dir = os.path.join(settings.BASE_DIR, 'docs', 'help')
        help_docs = []
        
        if os.path.exists(docs_dir):
            for filename in os.listdir(docs_dir):
                if filename.endswith('.md'):
                    filepath = os.path.join(docs_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        help_docs.append({
                            'title': filename.replace('.md', '').replace('_', ' ').title(),
                            'content': content,
                            'source': filename
                        })
            
            if help_docs:
                self.stdout.write(f"Found {len(help_docs)} help documents. Indexing...")
                indexer.index_help_docs(help_docs)
            else:
                self.stdout.write(self.style.WARNING("No markdown files found in docs/help/"))
        else:
            self.stdout.write(self.style.WARNING(f"Directory not found: {docs_dir}"))

        # 2. Index Clubs
        self.stdout.write("Indexing active clubs...")
        indexer.index_clubs()
        
        self.stdout.write(self.style.SUCCESS("✅ Indexing complete!"))