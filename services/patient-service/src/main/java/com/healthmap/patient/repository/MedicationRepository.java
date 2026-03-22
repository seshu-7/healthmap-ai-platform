package com.healthmap.patient.repository;

import com.healthmap.patient.entity.Medication;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface MedicationRepository extends JpaRepository<Medication, String> {

    List<Medication> findByPatientIdAndIsActiveTrue(String patientId);

    List<Medication> findByPatientId(String patientId);
}
