import { strategies } from './highlight';

export function highlight(code, lang) {
    if (!code) return '';
    const escaped = escapeHTML(code);
    return strategies[lang]?.(escaped) ?? escaped;
}

function escapeHTML(code) {
    return code
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
