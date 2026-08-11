// PromptShrink Extension Background Service Worker

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'promptshrink-context-menu',
    title: '🗜️ Otimizar prompt selecionado',
    contexts: ['selection'],
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'promptshrink-context-menu' && info.selectionText) {
    chrome.tabs.sendMessage(tab.id, {
      action: 'shrink_selection',
      text: info.selectionText,
    });
  }
});
