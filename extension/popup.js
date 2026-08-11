// PromptShrink Extension Popup Logic

document.addEventListener('DOMContentLoaded', () => {
  const statTokens = document.getElementById('statTokens');
  const statCost = document.getElementById('statCost');
  const selectLevel = document.getElementById('selectLevel');
  const togglePii = document.getElementById('togglePii');
  const toggleEmojis = document.getElementById('toggleEmojis');

  // Carrega configurações do storage
  if (chrome.storage && chrome.storage.local) {
    chrome.storage.local.get(['level', 'maskPii', 'stripEmojis', 'totalTokensSaved'], (res) => {
      if (res.level) selectLevel.value = res.level;
      if (res.maskPii !== undefined) togglePii.checked = res.maskPii;
      if (res.stripEmojis !== undefined) toggleEmojis.checked = res.stripEmojis;
      if (res.totalTokensSaved) {
        statTokens.innerText = res.totalTokensSaved.toLocaleString();
        const estCost = (res.totalTokensSaved / 1000000) * 2.5; // ~$2.50/1M tokens avg
        statCost.innerText = `$${estCost.toFixed(3)}`;
      }
    });
  }

  // Salva alterações nas opções
  function saveSettings() {
    if (chrome.storage && chrome.storage.local) {
      chrome.storage.local.set({
        level: selectLevel.value,
        maskPii: togglePii.checked,
        stripEmojis: toggleEmojis.checked,
      });
    }
  }

  selectLevel.addEventListener('change', saveSettings);
  togglePii.addEventListener('change', saveSettings);
  toggleEmojis.addEventListener('change', saveSettings);
});
