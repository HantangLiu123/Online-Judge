import { defineStore } from "pinia";
import api from '@/api/request.js';
import router from '@/router/index.js';

export const useUserStore = defineStore("user", {
    state: () => ({
        user: null,
        isLoggedIn: false,
    }),
    actions: {
        loginSuccess(userData) {
            this.user = userData;
            this.isLoggedIn = true;
        },
        async logout() {
            try {
                api.post('/auth/logout');
                this.user = null;
                this.isLoggedIn = false;
                router.push('/auth/login');
            } catch (error) {
                console.error("Logout failed:", error);
            }

        },
    },
    persist: true,
});