<template>
  <div class="pagination">
    <button
      :disabled="currentPage === 1"
      @click="changePage(currentPage - 1)"
    >
      previous
    </button>

    <button
      v-for="page in pages"
      :key="page"
      :class="{ active: page === currentPage }"
      @click="changePage(page)"
    >
      {{ page }}
    </button>

    <button
      :disabled="currentPage === totalPages"
      @click="changePage(currentPage + 1)"
    >
      next
    </button>
  </div>
</template>

<script>
export default {
  name: 'Pagination',

  props: {
    currentPage: {
      type: Number,
      required: true
    },
    pageSize: {
      type: Number,
      required: true
    },
    total: {
      type: Number,
      required: true
    },
    totalPages: {
      type: Number,
      required: true
    }
  },

  computed: {
    pages() {
      return Array.from(
        { length: this.totalPages },
        (_, i) => i + 1
      );
    }
  },

  methods: {
    changePage(page) {
      if (page < 1 || page > this.totalPages) return;
      this.$emit('update:currentPage', page);
    }
  }
};
</script>

<style scoped>
.pagination {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}

button {
  padding: 4px 10px;
  cursor: pointer;
}

button.active {
  background-color: #409eff;
  color: white;
  font-weight: bold;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
