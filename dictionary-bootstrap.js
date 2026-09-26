// Prevent the legacy qwerty-learner dictionary loader in app.js from making a network request.
// The actual dictionary UI is replaced by dictionary-wiktionary.js after app.js loads.
try{localStorage.setItem('river.ngsl.dict','{}')}catch(e){}
