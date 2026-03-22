package com.healthmap.patient.service;

import com.healthmap.patient.dto.LabResultDto;
import com.healthmap.patient.entity.LabResult;
import com.healthmap.patient.repository.LabResultRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageRequest;
import java.time.LocalDate;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class LabResultServiceTest {

    @Mock private LabResultRepository repo;
    @InjectMocks private LabResultService service;

    @Test
    void getByPatient_returnsLimitedResults() {
        LabResult lab = LabResult.builder().id("L001").patientId("P001")
            .testName("eGFR").value(22.0).unit("mL/min").isAbnormal(true)
            .collectedDate(LocalDate.of(2024, 10, 15)).build();
        when(repo.findByPatientIdOrderByCollectedDateDesc("P001", PageRequest.of(0, 5)))
            .thenReturn(List.of(lab));

        List<LabResultDto> results = service.getByPatient("P001", 5);
        assertEquals(1, results.size());
        assertEquals("eGFR", results.get(0).getTestName());
        assertEquals(22.0, results.get(0).getValue());
    }

    @Test
    void getAbnormal_onlyReturnsAbnormal() {
        LabResult abnormal = LabResult.builder().id("L001").patientId("P001")
            .testName("Potassium").value(5.8).isAbnormal(true).build();
        when(repo.findByPatientIdAndIsAbnormalTrue("P001")).thenReturn(List.of(abnormal));

        List<LabResultDto> results = service.getAbnormalByPatient("P001");
        assertEquals(1, results.size());
        assertTrue(results.get(0).getIsAbnormal());
    }
}
