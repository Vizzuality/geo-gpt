
async function renderMarkdown(markdownText) {
    const marked = await import('https://cdn.jsdelivr.net/npm/marked/marked.min.js');
    return marked(markdownText);
  }
  
  export { renderMarkdown };
  