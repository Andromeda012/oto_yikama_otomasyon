import { createRouter, createWebHistory } from "vue-router";
import PlaceholderView from "../views/PlaceholderView.vue";
import DashboardView from "../views/DashboardView.vue";
import AppointmentView from "../views/AppointmentView.vue";
import DefinitionsView from "../views/DefinitionsView.vue";
import VehicleTrackingView from "../views/VehicleTrackingView.vue";
import MarketView from "../views/MarketView.vue";
import CompanyAccountView from "../views/CompanyAccountView.vue";
import SettingsView from "../views/SettingsView.vue";
import StatisticsView from "../views/StatisticsView.vue";
import CustomerView from "../views/CustomerView.vue";
import AdminLoginView from "../views/AdminLoginView.vue";
import CustomerBookingView from "../views/CustomerBookingView.vue";
import CustomerTrackingView from "../views/CustomerTrackingView.vue";
import CustomerSimpleView from "../views/CustomerSimpleView.vue";
import CustomerAccountView from "../views/CustomerAccountView.vue";
import { getCurrentUser } from "../services/auth";

const admin = (path, name, component) => ({ path, name, component, meta: { requiresAuth: true } });

const routes = [
  { path: "/", name: "customer", component: CustomerView, meta: { public: true } },
  { path: "/admin/login", name: "admin-login", component: AdminLoginView, meta: { public: true } },
  { path: "/musteri", redirect: "/", meta: { public: true } },
  { path: "/musteri/randevu-al", name: "customer-booking", component: CustomerBookingView, meta: { public: true } },
  { path: "/musteri/randevu-takip", name: "customer-tracking", component: CustomerTrackingView, meta: { public: true } },
  { path: "/musteri/hesabim", name: "customer-account", component: CustomerAccountView, meta: { public: true } },
  { path: "/musteri/ayarlar", name: "customer-settings", component: CustomerSimpleView, props: { title: "Ayarlar", icon: "⚙", message: "Müşteri ayarları bu alanda geliştirilecek." }, meta: { public: true } },
  { path: "/admin", redirect: "/admin/dashboard", meta: { requiresAuth: true } },
  admin("/admin/dashboard", "dashboard", DashboardView),
  admin("/admin/hesabim", "account", CompanyAccountView),
  { path: "/admin/cari", redirect: "/admin/tanimlar/cari", meta: { requiresAuth: true } },
  admin("/admin/ayarlar/:subsection?", "settings", SettingsView),
  admin("/admin/tanimlar/:subsection?", "definitions", DefinitionsView),
  admin("/admin/yonetim/market", "market", MarketView),
  admin("/admin/yonetim/arac-takip", "operations", VehicleTrackingView),
  admin("/admin/yonetim/randevu", "appointments", AppointmentView),
  admin("/admin/istatistikler/:subsection?", "statistics", StatisticsView),
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) return true;
  try {
    await getCurrentUser();
    return true;
  } catch {
    return { name: "admin-login", query: { redirect: to.fullPath } };
  }
});

export default router;
