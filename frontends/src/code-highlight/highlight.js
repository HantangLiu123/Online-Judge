export function pythonHighlight(code) {
    code = code.replace(
        /\b(def|return|if|else|elif|for|while|import|from|class|print|in|and|or|not)\b/g,
        '<span class="kw">$1</span>'
    );

    code = code.replace(
        /(&quot;.*?&quot;|&#39;.*?&#39;)/g,
        '<span class="str">$1</span>'
    );

    code = code.replace(/\b\d+\b/g, '<span class="num">$&</span>');

    return code;
}

export function cppHighlight(code) {
    code = code.replace(
        /\b(int|long|double|float|if|else|for|while|return|class|struct|include|using|namespace)\b/g,
        '<span class="kw">$1</span>'
    );

    code = code.replace(
        /&quot;.*?&quot;/g,
        '<span class="str">$&</span>'
    );

    code = code.replace(/\b\d+\b/g, '<span class="num">$&</span>');

    return code;
}

export const strategies = {
    python: pythonHighlight,
    cpp: cppHighlight,
};
