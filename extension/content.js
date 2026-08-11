/**
 * PromptShrink Content Script — Inject Floating Shrink Button into Web AI Interfaces
 */

(function () {
  'use strict';

  const API_ENDPOINT = 'http://localhost:8000/v1/optimize';

  // ---------------------------------------------------------------------------
  // Fast Local Fallback Engine (Client-side regex optimizer)
  // ---------------------------------------------------------------------------

  function fastLocalOptimize(text) {
    let current = text;
    // Cortesias
    current = current.replace(/\b(olá|oi|hey|bom dia|boa tarde|boa noite)[,!.]?\s*(tudo bem\??|como vai\??)?\s*/gi, '');
    current = current.replace(/\b(hi|hello|hey|good morning|good afternoon)[,!.]?\s*(hope you're doing well)?\s*/gi, '');
    // Fechamentos
    current = current.replace(/\s*(obrigad[oa]|muito obrigad[oa]|agradeço|atenciosamente)[. !]*$/gi, '');
    current = current.replace(/\s*(thanks|thank you|best regards|cheers)[. !]*$/gi, '');
    // Verbosidades
    current = current.replace(/por favor,\s*(você poderia|poderia você|pode você)\s*/gi, '');
    current = current.replace(/\b(basicamente|simplesmente|literalmente|actually|basically)\b,?\s*/gi, '');
    // Espaços
    current = current.replace(/[ \t]{2,}/g, ' ').replace(/\n{3,}/g, '\n\n').trim();

    const origTokens = Math.max(1, Math.round(text.split(/\s+/).length * 1.3));
    const optTokens = Math.max(1, Math.round(current.split(/\s+/).length * 1.3));
    const saved = Math.max(0, origTokens - optTokens);
    const percent = Math.round((saved / origTokens) * 100);

    return {
      optimizedText: current,
      tokensSaved: saved,
      percentSaved: percent,
    };
  }

  // ---------------------------------------------------------------------------
  // UI Helpers
  // ---------------------------------------------------------------------------

  function showToast(message, badgeText = 'REDUZIDO') {
    const existing = document.querySelector('.promptshrink-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'promptshrink-toast';
    toast.innerHTML = `<span class="ps-badge">🗜️ ${badgeText}</span> <span>${message}</span>`;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.transition = 'opacity 0.4s ease';
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 400);
    }, 3500);
  }

  function getActiveInputField() {
    // 1. ChatGPT
    const chatGptInput = document.querySelector('#prompt-textarea') || document.querySelector('div[contenteditable="true"]');
    if (chatGptInput) return chatGptInput;

    // 2. Claude / Poe / Generic Textarea
    const textareas = document.querySelectorAll('textarea, div[contenteditable="true"]');
    for (const ta of textareas) {
      if (ta.offsetWidth > 0 && ta.offsetHeight > 0) return ta;
    }
    return null;
  }

  function getInputText(field) {
    if (!field) return '';
    return field.tagName === 'TEXTAREA' || field.tagName === 'INPUT' ? field.value : field.innerText;
  }

  function setInputText(field, newText) {
    if (!field) return;
    if (field.tagName === 'TEXTAREA' || field.tagName === 'INPUT') {
      field.value = newText;
    } else {
      field.innerText = newText;
    }
    field.dispatchEvent(new Event('input', { bubbles: true }));
    field.dispatchEvent(new Event('change', { bubbles: true }));
  }

  // ---------------------------------------------------------------------------
  // Optimization Trigger
  // ---------------------------------------------------------------------------

  async function handleShrinkClick(btn) {
    const field = getActiveInputField();
    if (!field) {
      showToast('Caixa de texto não encontrada.', 'ERRO');
      return;
    }

    const text = getInputText(field);
    if (!text.trim()) {
      showToast('Digite um prompt primeiro.', 'AVISO');
      return;
    }

    btn.classList.add('loading');
    btn.innerText = '⏳ Otimizando…';

    try {
      // Tenta chamar API backend
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          model: 'gpt-4o',
          level: 'moderate',
          semantic: true,
          mask_pii_data: false,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setInputText(field, data.optimized.text);
        showToast(`-${data.savings.tokens} tokens (-${data.savings.percent.toFixed(1)}%) economizados!`, 'SUCESSO');
      } else {
        throw new Error('API offline');
      }
    } catch (err) {
      // Fallback local caso API esteja offline
      const localRes = fastLocalOptimize(text);
      setInputText(field, localRes.optimizedText);
      showToast(`-${localRes.tokensSaved} tokens (-${localRes.percentSaved}%) economizados!`, 'LOCAL');
    } finally {
      btn.classList.remove('loading');
      btn.innerHTML = '🗜️ Shrink';
    }
  }

  // ---------------------------------------------------------------------------
  // Button Injection Loop
  // ---------------------------------------------------------------------------

  function injectButton() {
    if (document.querySelector('.promptshrink-btn')) return;

    const field = getActiveInputField();
    if (!field) return;

    const parent = field.parentElement;
    if (!parent) return;

    const btn = document.createElement('button');
    btn.className = 'promptshrink-btn';
    btn.innerHTML = '🗜️ Shrink';
    btn.title = 'PromptShrink — Clique para minificar e otimizar tokens';
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      handleShrinkClick(btn);
    });

    parent.appendChild(btn);
  }

  // Observa mudanças no DOM
  const observer = new MutationObserver(() => injectButton());
  observer.observe(document.body, { childList: true, subtree: true });
  injectButton();
})();
