package com.healthmap.patient.repository;

import com.healthmap.patient.entity.Patient;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface PatientRepository extends JpaRepository<Patient, String> {

    List<Patient> findByAssignedCoordinator(String coordinatorId);

    List<Patient> findByPrimaryCondition(String condition);

    @Query("SELECT p FROM Patient p WHERE LOWER(p.firstName) LIKE LOWER(CONCAT('%',:q,'%')) " +
           "OR LOWER(p.lastName) LIKE LOWER(CONCAT('%',:q,'%')) " +
           "OR LOWER(p.conditions) LIKE LOWER(CONCAT('%',:q,'%'))")
    List<Patient> search(String q);
}
