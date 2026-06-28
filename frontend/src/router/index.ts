import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'
import CreateRunView from '../views/CreateRunView.vue'
import DashboardView from '../views/DashboardView.vue'
import ProviderConfigsView from '../views/ProviderConfigsView.vue'
import RunDetailView from '../views/RunDetailView.vue'
import SuiteDetailView from '../views/SuiteDetailView.vue'
import SuitesView from '../views/SuitesView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        { path: '', name: 'dashboard', component: DashboardView },
        { path: 'providers', name: 'providers', component: ProviderConfigsView },
        { path: 'suites', name: 'suites', component: SuitesView },
        { path: 'suites/:id', name: 'suite-detail', component: SuiteDetailView, props: true },
        { path: 'runs', name: 'runs', component: CreateRunView },
        { path: 'runs/:id', name: 'run-detail', component: RunDetailView, props: true },
      ],
    },
  ],
})

export default router
