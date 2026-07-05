import { reactive } from 'vue';

const state = reactive({
    languages: [],
    rejudgeQueue: [],
});

const addLanguage = (newLanguage) => {
    state.languages.push(newLanguage);
};

const addToRejudgeQueue = (submissionId) => {
    state.rejudgeQueue.push(submissionId);
};

export default { state, addLanguage, addToRejudgeQueue };