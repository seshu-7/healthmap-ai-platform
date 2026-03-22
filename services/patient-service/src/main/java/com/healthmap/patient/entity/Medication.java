package com.healthmap.patient.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;

@Entity
@Table(name = "medications")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class Medication {

    @Id
    @Column(length = 36)
    private String id;

    @Column(name = "patient_id", nullable = false)
    private String patientId;

    @Column(name = "drug_name", nullable = false)
    private String drugName;

    private String dosage;
    private String frequency;
    private String prescriber;

    @Column(name = "start_date")
    private LocalDate startDate;

    @Column(name = "is_active")
    private Boolean isActive;
}
