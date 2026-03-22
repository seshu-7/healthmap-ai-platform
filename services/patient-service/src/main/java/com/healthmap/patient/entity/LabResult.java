package com.healthmap.patient.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;

@Entity
@Table(name = "lab_results")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class LabResult {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "patient_id", nullable = false)
    private String patientId;

    @Column(name = "test_name", nullable = false)
    private String testName;

    @Column(name = "result_value", nullable = false)
    private Double value;

    private String unit;

    @Column(name = "reference_range")
    private String referenceRange;

    @Column(name = "is_abnormal")
    private Boolean isAbnormal;

    @Column(name = "collected_date")
    private LocalDate collectedDate;
}
