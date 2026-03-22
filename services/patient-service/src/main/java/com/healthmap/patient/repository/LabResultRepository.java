package com.healthmap.patient.repository;

import com.healthmap.patient.entity.LabResult;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface LabResultRepository extends JpaRepository<LabResult, String> {

    List<LabResult> findByPatientIdOrderByCollectedDateDesc(String patientId, Pageable pageable);

    List<LabResult> findByPatientIdAndIsAbnormalTrue(String patientId);
}
