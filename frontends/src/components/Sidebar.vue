<template>
  <aside class="sidebar">
    <ul>
      <li><router-link to="/problems">Problems</router-link></li>
      <li><router-link to="/submissions">Submissions</router-link></li>
      <li v-if="isAdmin"><router-link to="/admin/add-language">Add Language</router-link></li>
      <li v-if="isAdmin"><router-link to="/admin/rejudge">Rejudge</router-link></li>
    </ul>
  </aside>
</template>

<script>
import { computed } from 'vue';
import authStore from '../store/auth';

export default {
  setup() {
    const isAdmin = computed(() => authStore.state.user?.role === 'admin');
    return { isAdmin };
  }
};
</script>

<style>
.sidebar {
  width: 200px;
  background: #f4f4f4;
  padding: 10px;
}
.sidebar ul {
  list-style: none;
  padding: 0;
}
.sidebar a {
  display: block;
  padding: 5px 10px;
  text-decoration: none;
  color: #333;
}
.sidebar a:hover {
  background: #ddd;
}
</style>