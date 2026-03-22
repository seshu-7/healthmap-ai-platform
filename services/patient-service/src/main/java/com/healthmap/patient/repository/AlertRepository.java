package com.healthmap.patient.repository;

import com.healthmap.patient.entity.Alert;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface AlertRepository extends JpaRepository<Alert, String> {

    List<Alert> findByPatientIdOrderByCreatedAtDesc(String patientId);

    List<Alert> findByStatusOrderByCreatedAtDesc(String status);
}
