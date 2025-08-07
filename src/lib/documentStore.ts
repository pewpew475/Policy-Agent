// Simple in-memory document store
// In production, this would be replaced with a database like PostgreSQL or Redis

class DocumentStore {
  private store = new Map<string, string>()

  set(documentId: string, content: string): void {
    this.store.set(documentId, content)
    console.log(`Stored document ${documentId} with ${content.length} characters`)
  }

  get(documentId: string): string | undefined {
    const content = this.store.get(documentId)
    console.log(`Retrieved document ${documentId}: ${content ? `${content.length} characters` : 'not found'}`)
    return content
  }

  getMultiple(documentIds: string[]): string {
    const contents: string[] = []
    
    for (const id of documentIds) {
      const content = this.get(id)
      if (content) {
        contents.push(`Document ${id}:\n${content}`)
      }
    }
    
    return contents.join('\n\n---\n\n')
  }

  has(documentId: string): boolean {
    return this.store.has(documentId)
  }

  delete(documentId: string): boolean {
    return this.store.delete(documentId)
  }

  clear(): void {
    this.store.clear()
  }

  size(): number {
    return this.store.size
  }
}

// Export a singleton instance
export const documentStore = new DocumentStore()
