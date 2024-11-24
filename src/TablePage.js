import React, { useState } from "react";
import { Table, Button, Badge, Pagination, Form } from "react-bootstrap";
import { useNavigate } from "react-router-dom"; // Import useNavigate

const TablePage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [majorFilter, setMajorFilter] = useState("");
  const [sortOption, setSortOption] = useState("name"); // Default sort by name

  const navigate = useNavigate(); // Hook untuk navigasi

  const students = [
    { name: "Olivia Rhye", npm: "2031122", status: "Lulus", major: "Sistem Informasi", gpa: 3.8 },
    { name: "Phoenix Baker", npm: "2341155", status: "Aktif", major: "Manajemen", gpa: 3.78 },
    { name: "Candice Wu", npm: "2351151", status: "NonAktif", major: "Hukum", gpa: 3.87 },
    { name: "Natali Craig", npm: "2461165", status: "Aktif", major: "Teknik Sipil", gpa: 3.98 },
    { name: "Drew Cano", npm: "2111546", status: "Aktif", major: "Teknik Informatika", gpa: 3.96 },
    { name: "Nayara", npm: "2121546", status: "Aktif", major: "Akuntansi", gpa: 3.76 },
    { name: "Giandra", npm: "2101546", status: "Aktif", major: "Arsitektur", gpa: 3.86 },
    { name: "Vania", npm: "2271546", status: "Aktif", major: "Pariwisata", gpa: 3.56 },
  ];

  const getStatusBadge = (status) => {
    switch (status) {
      case "Lulus":
        return <Badge bg="success">Lulus</Badge>;
      case "Aktif":
        return <Badge bg="primary">Aktif</Badge>;
      case "NonAktif":
        return <Badge bg="danger">NonAktif</Badge>;
      default:
        return <Badge bg="secondary">Unknown</Badge>;
    }
  };

  const uniqueMajors = [...new Set(students.map((student) => student.major))];

  const filteredStudents = students
    .filter(
      (student) =>
        (student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          student.npm.includes(searchTerm)) &&
        (statusFilter === "" || student.status === statusFilter) &&
        (majorFilter === "" || student.major === majorFilter)
    )
    .sort((a, b) => {
      if (sortOption === "name") {
        return a.name.localeCompare(b.name);
      } else if (sortOption === "gpa") {
        return b.gpa - a.gpa;
      }
      return 0;
    });

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <input
          type="text"
          className="form-control w-25"
          placeholder="Search by name or NPM..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />

        <Form.Select
          className="w-25"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">Filter by Status</option>
          <option value="Lulus">Lulus</option>
          <option value="Aktif">Aktif</option>
          <option value="NonAktif">NonAktif</option>
        </Form.Select>

        <Form.Select
          className="w-25"
          value={majorFilter}
          onChange={(e) => setMajorFilter(e.target.value)}
        >
          <option value="">Filter by Major</option>
          {uniqueMajors.map((major, index) => (
            <option key={index} value={major}>
              {major}
            </option>
          ))}
        </Form.Select>

        <Form.Select
          className="w-25"
          value={sortOption}
          onChange={(e) => setSortOption(e.target.value)}
        >
          <option value="name">Sort by Name (A-Z)</option>
          <option value="gpa">Sort by GPA (High to Low)</option>
        </Form.Select>
      </div>

      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Name/NPM</th>
            <th>Status</th>
            <th>Jurusan</th>
            <th>IPK</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          {filteredStudents.map((student, index) => (
            <tr key={index}>
              <td>
                {student.name} <br /> {student.npm}
              </td>
              <td>{getStatusBadge(student.status)}</td>
              <td>{student.major}</td>
              <td>{student.gpa.toFixed(2)}</td>
              <td>
                <Button
                  variant="outline-primary"
                  size="sm"
                  onClick={() =>
                    navigate("/kategorisasi", {
                      state: student, // Kirim data mahasiswa ke halaman Kategorisasi
                    })
                  }
                >
                  Kategorisasi
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      <Pagination>
        <Pagination.Prev />
        <Pagination.Item active>{1}</Pagination.Item>
        <Pagination.Item>{2}</Pagination.Item>
        <Pagination.Next />
      </Pagination>
    </div>
  );
};

export default TablePage;
