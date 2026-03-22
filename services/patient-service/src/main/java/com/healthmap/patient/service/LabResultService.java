package com.healthmap.patient.service;

import com.healthmap.patient.dto.LabResultDto;
import com.healthmap.patient.entity.LabResult;
import com.healthmap.patient.repository.LabResultRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@RequiredArgsConstructor
public class LabResultService {

    private final LabResultRepository repo;

    public List<LabResultDto> getByPatient(String patientId, int limit) {
        return repo.findByPatientIdOrderByCollectedDateDesc(patientId, PageRequest.of(0, limit))
            .stream().map(this::toDto).toList();
    }

    public List<LabResultDto> getAbnormalByPatient(String patientId) {
        return repo.findByPatientIdAndIsAbnormalTrue(patientId)
            .stream().map(this::toDto).toList();
    }

    private LabResultDto toDto(LabResult l) {
        return LabResultDto.builder()
            .labId(l.getId()).patientId(l.getPatientId())
            .testName(l.getTestName()).value(l.getValue())
            .unit(l.getUnit()).referenceRange(l.getReferenceRange())
            .isAbnormal(l.getIsAbnormal())
            .collectedDate(l.getCollectedDate() != null ? l.getCollectedDate().toString() : null)
            .build();
    }
}
