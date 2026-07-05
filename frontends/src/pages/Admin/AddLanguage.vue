<template>
  <div>
    <h1>Add New Language</h1>
    <form @submit.prevent="addLanguage">
      <label for="name">Language Name:</label>
      <input id="name" v-model="languageName" type="text" required />
      <label for="image">Image Name:</label>
      <input id="image" v-model="imageName" type="text" required />
      <button type="submit">Add Language</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      languageName: '',
      imageName: ''
    };
  },
  methods: {
    async addLanguage() {
      try {
        // Call the API to add a new language
        alert(`Language ${this.languageName} added successfully!`);
        this.languageName = '';
        this.imageName = '';
      } catch (error) {
        console.error(error);
        alert('Failed to add language');
      }
    }
  }
};
</script>