import React from "react";
import { useLocation } from "react-router-dom"; // Import useLocation
import Card from "./Card";
import { Card as BootstrapCard, Container } from "react-bootstrap"; // Import komponen Bootstrap

const Kategorisasi = () => {
  const location = useLocation();
  const student = location.state; // Ambil data mahasiswa dari state

  return (
    <Container>
      <h1>Kategorisasi</h1>

      {student && (
        <BootstrapCard
          className="shadow-sm mb-4"
          style={{
            border: "1px solid #ddd",
            borderRadius: "8px",
            padding: "20px",
          }}
        >
          <h3 className="mb-3"> Data Mahasiswa</h3>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "150px 20px 1fr", // Kolom label, titik dua, dan nilai
              rowGap: "10px",
              alignItems: "center",
            }}
          >
            <div><strong>Nama</strong></div>
            <div>:</div>
            <div>{student.name}</div>

            <div><strong>NPM</strong></div>
            <div>:</div>
            <div>{student.npm}</div>

            <div><strong>Status</strong></div>
            <div>:</div>
            <div
              style={{
                color:
                  student.status === "Lulus"
                    ? "green"
                    : student.status === "NonAktif"
                    ? "red"
                    : "blue",
                fontWeight: "bold",
              }}
            >
              {student.status}
            </div>

            <div><strong>Jurusan</strong></div>
            <div>:</div>
            <div>{student.major}</div>

            <div><strong>IPK</strong></div>
            <div>:</div>
            <div style={{ fontWeight: "bold" }}>{student.gpa.toFixed(2)}</div>
          </div>
        </BootstrapCard>
      )}

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "20px", // Jarak antar kartu
          padding: "20px",
        }}
      >
        <Card title="Kelulusan" bgColor="green" />
        <Card title="Kegiatan Mahasiswa" bgColor="blue" />
        <Card title="Peminatan Mahasiswa" bgColor="gold" />
      </div>
    </Container>
  );
};

export default Kategorisasi;
