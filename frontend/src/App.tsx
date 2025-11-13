import { BrowserRouter, Route, Routes } from "react-router-dom";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import CoursePage from "./pages/CoursePage";
import InstitutionPage from "./pages/InstitutionPage";
import LoginPage from "./pages/LoginPage";
import ProfessorPage from "./pages/ProfessorPage";
import RegisterPage from "./pages/RegisterPage";
import ReviewCreatePage from "./pages/ReviewCreatePage";
import SubjectPage from "./pages/SubjectPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/institutions/:institutionId" element={<InstitutionPage />} />
        <Route path="/courses/:courseId" element={<CoursePage />} />
        <Route path="/professors/:professorId" element={<ProfessorPage />} />
        <Route path="/subjects/:subjectId" element={<SubjectPage />} />
        <Route path="/reviews/new" element={<ReviewCreatePage />} />
        <Route path="/admin" element={<AdminDashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
