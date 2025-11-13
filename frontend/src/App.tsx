import { BrowserRouter, Route, Routes } from "react-router-dom";
import AdminLayout from "./layouts/AdminLayout";
import AuthLayout from "./layouts/AuthLayout";
import MainLayout from "./layouts/MainLayout";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import CoursePage from "./pages/CoursePage";
import HomePage from "./pages/HomePage";
import InstitutionPage from "./pages/InstitutionPage";
import LoginPage from "./pages/LoginPage";
import NotFoundPage from "./pages/NotFoundPage";
import ProfessorPage from "./pages/ProfessorPage";
import RegisterPage from "./pages/RegisterPage";
import ReviewCreatePage from "./pages/ReviewCreatePage";
import SubjectPage from "./pages/SubjectPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route index element={<HomePage />} />
          <Route path="/institutions/:institutionId" element={<InstitutionPage />} />
          <Route path="/courses/:courseId" element={<CoursePage />} />
          <Route path="/professors/:professorId" element={<ProfessorPage />} />
          <Route path="/subjects/:subjectId" element={<SubjectPage />} />
          <Route path="/reviews/new" element={<ReviewCreatePage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>
        <Route element={<AdminLayout />}>
          <Route path="/admin" element={<AdminDashboardPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
