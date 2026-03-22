package com.healthmap.patient.service;

import com.healthmap.patient.dto.MedicationDto;
import com.healthmap.patient.entity.Medication;
import com.healthmap.patient.repository.MedicationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@RequiredArgsConstructor
public class MedicationService {

    private final MedicationRepository repo;

    public List<MedicationDto> getByPatient(String patientId, boolean activeOnly) {
        List<Medication> meds = activeOnly
            ? repo.findByPatientIdAndIsActiveTrue(patientId)
            : repo.findByPatientId(patientId);
        return meds.stream().map(this::toDto).toList();
    }

    private MedicationDto toDto(Medication m) {
        return MedicationDto.builder()
            .medicationId(m.getId()).patientId(m.getPatientId())
            .drugName(m.getDrugName()).dosage(m.getDosage())
            .frequency(m.getFrequency()).prescriber(m.getPrescriber())
            .startDate(m.getStartDate() != null ? m.getStartDate().toString() : null)
            .isActive(m.getIsActive())
            .build();
    }
}
