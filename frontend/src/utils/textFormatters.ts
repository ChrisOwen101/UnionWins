/**
 * Filter out citations from text
 * Removes markdown links, text in parentheses, and URLs in brackets
 * Examples: [text](url), (citation text), (www.XYZ.com)
 */
export const filterCitations = (text: string): string => {
    if (!text) return text

    // Remove markdown links: [text](url)
    let filtered = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')

    // Remove URLs in brackets: (www.example.com) or (https://example.com)
    filtered = filtered.replace(/\s*\((?:https?:\/\/)?(?:www\.)?[^\s)]+\.[^\s)]+\)\s*/g, ' ')

    // Remove citations in parentheses at the end of sentences or phrases
    // This pattern matches (text) that appears after punctuation or at sentence end
    filtered = filtered.replace(/\s*\([^)]*\)\s*$/gm, '')

    // Clean up any remaining multiple spaces
    filtered = filtered.replace(/\s+/g, ' ').trim()

    return filtered
}
