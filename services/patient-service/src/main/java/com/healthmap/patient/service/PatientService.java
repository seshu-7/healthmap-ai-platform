package com.healthmap.patient.service;

import com.healthmap.patient.dto.PatientDto;
import com.healthmap.patient.entity.Patient;
import com.healthmap.patient.exception.ResourceNotFoundException;
import com.healthmap.patient.repository.PatientRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.Arrays;
import java.util.List;

@Service
@RequiredArgsConstructor
public class PatientService {

    private final PatientRepository repo;

    public PatientDto getById(String id) {
        Patient p = repo.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Patient", id));
        return toDto(p);
    }

    public List<PatientDto> search(String query) {
        return repo.search(query).stream().map(this::toDto).toList();
    }

    public List<PatientDto> getByCoordinator(String coordinatorId) {
        return repo.findByAssignedCoordinator(coordinatorId).stream().map(this::toDto).toList();
    }

    public PatientDto create(PatientDto dto) {
        Patient p = Patient.builder()
            .id(dto.getPatientId())
            .firstName(dto.getFirstName())
            .lastName(dto.getLastName())
            .dateOfBirth(dto.getDateOfBirth() != null ? java.time.LocalDate.parse(dto.getDateOfBirth()) : null)
            .gender(dto.getGender())
            .primaryCondition(dto.getPrimaryCondition())
            .conditions(dto.getConditions() != null ? String.join(",", dto.getConditions()) : "")
            .insurancePlan(dto.getInsurancePlan())
            .assignedCoordinator(dto.getAssignedCoordinator())
            .build();
        return toDto(repo.save(p));
    }

    private PatientDto toDto(Patient p) {
        return PatientDto.builder()
            .patientId(p.getId())
            .firstName(p.getFirstName())
            .lastName(p.getLastName())
            .dateOfBirth(p.getDateOfBirth() != null ? p.getDateOfBirth().toString() : null)
            .gender(p.getGender())
            .primaryCondition(p.getPrimaryCondition())
            .conditions(p.getConditions() != null ? Arrays.asList(p.getConditions().split(",")) : List.of())
            .insurancePlan(p.getInsurancePlan())
            .assignedCoordinator(p.getAssignedCoordinator())
            .build();
    }
}
