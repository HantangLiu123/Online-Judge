<template>
  <div v-if="errorMessage" class="error-container">
    <div class="error-message">
      <p><strong>Error:</strong> {{ errorMessage }}</p>
      <button @click="clearError">Dismiss</button>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  setup() {
    const errorMessage = ref(null);

    // A function to simulate setting an error (this can be replaced with a global event-based approach)
    const setError = (message) => {
      errorMessage.value = message;
    };

    const clearError = () => {
      errorMessage.value = null;
    };

    // For demonstration purposes: you can listen for global error events
    // For example, via an event bus or an error store
    return { errorMessage, setError, clearError };
  },
};
</script>

<style>
.error-container {
  position: fixed;
  top: 10px;
  right: 10px;
  width: 300px;
  background-color: #ffdddd;
  color: #a60000;
  border: 1px solid #a60000;
  padding: 15px;
  border-radius: 8px;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.error-message p {
  margin: 0;
  font-size: 14px;
}

.error-message button {
  margin-top: 10px;
  background-color: #a60000;
  color: #fff;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.error-message button:hover {
  background-color: #d10000;
}
</style>