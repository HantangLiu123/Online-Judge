import { createRouter, createWebHistory } from 'vue-router';
import Login from '../pages/Auth/Login.vue';
import Register from '../pages/Auth/Register.vue';
import ProblemList from '../pages/Problems/ProblemList.vue';
import ProblemDetail from '../pages/Problems/ProblemDetail.vue';
import ManageUsers from '../pages/Admin/ManageUsers.vue';
import UserDetail from '../pages/Users/UserDetail.vue';
import SubmissionList from '../pages/Submissions/SubmissionList.vue';
import SubmissionDetail from '../pages/Submissions/SubmissionDetail.vue';
import AddLanguage from '../pages/Admin/AddLanguage.vue';
import Error400 from '../pages/Errors/Error400.vue';
import Error401 from '../pages/Errors/Error401.vue';
import Error403 from '../pages/Errors/Error403.vue';
import Error404 from '../pages/Errors/Error404.vue';
import Error409 from '../pages/Errors/Error409.vue';
import Error429 from '../pages/Errors/Error429.vue';

const routes = [
  { path: '/', redirect: '/auth/login' },
  { path: '/auth/login', component: Login },
  { path: '/auth/register', component: Register },
  { path: '/problems', component: ProblemList },
  { path: '/problems/:id', component: ProblemDetail },
  { path: '/admin/manage-users', component: ManageUsers },
  { path: '/users/:id', component: UserDetail },
  { path: '/submissions', component: SubmissionList },
  { path: '/submissions/:id', component: SubmissionDetail },
  { path: '/admin/add-language', component: AddLanguage },
  { path: '/error/400', component: Error400 },
  { path: '/error/401', component: Error401 },
  { path: '/error/403', component: Error403 },
  { path: '/error/404', component: Error404 },
  { path: '/error/409', component: Error409 },
  { path: '/error/429', component: Error429 },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
