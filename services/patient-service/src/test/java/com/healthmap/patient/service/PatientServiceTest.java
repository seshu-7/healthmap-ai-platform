package com.healthmap.patient.service;

import com.healthmap.patient.dto.PatientDto;
import com.healthmap.patient.entity.Patient;
import com.healthmap.patient.exception.ResourceNotFoundException;
import com.healthmap.patient.repository.PatientRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import java.util.Optional;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PatientServiceTest {

    @Mock private PatientRepository repo;
    @InjectMocks private PatientService service;

    @Test
    void getById_existingPatient_returnsDto() {
        Patient p = Patient.builder().id("P001").firstName("John").lastName("Doe")
            .primaryCondition("CKD").conditions("CKD,hypertension").build();
        when(repo.findById("P001")).thenReturn(Optional.of(p));

        PatientDto dto = service.getById("P001");
        assertEquals("P001", dto.getPatientId());
        assertEquals("John", dto.getFirstName());
        assertEquals(List.of("CKD", "hypertension"), dto.getConditions());
    }

    @Test
    void getById_missingPatient_throwsException() {
        when(repo.findById("X")).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> service.getById("X"));
    }

    @Test
    void search_returnsMatchingPatients() {
        Patient p = Patient.builder().id("P001").firstName("John").lastName("Doe").conditions("CKD").build();
        when(repo.search("John")).thenReturn(List.of(p));

        List<PatientDto> results = service.search("John");
        assertEquals(1, results.size());
        assertEquals("P001", results.get(0).getPatientId());
    }

    @Test
    void getByCoordinator_returnsAssignedPatients() {
        Patient p1 = Patient.builder().id("P001").firstName("John").assignedCoordinator("C001").conditions("").build();
        Patient p2 = Patient.builder().id("P002").firstName("Jane").assignedCoordinator("C001").conditions("").build();
        when(repo.findByAssignedCoordinator("C001")).thenReturn(List.of(p1, p2));

        assertEquals(2, service.getByCoordinator("C001").size());
    }

    @Test
    void create_savesAndReturnsDto() {
        PatientDto input = PatientDto.builder().patientId("P010").firstName("New").lastName("Patient")
            .primaryCondition("diabetes").conditions(List.of("diabetes")).build();
        when(repo.save(any())).thenAnswer(inv -> inv.getArgument(0));

        PatientDto result = service.create(input);
        assertEquals("P010", result.getPatientId());
        verify(repo).save(any());
    }
}
