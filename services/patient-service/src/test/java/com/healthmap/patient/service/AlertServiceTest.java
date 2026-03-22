package com.healthmap.patient.service;

import com.healthmap.patient.dto.AlertDto;
import com.healthmap.patient.entity.Alert;
import com.healthmap.patient.repository.AlertRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AlertServiceTest {

    @Mock private AlertRepository repo;
    @InjectMocks private AlertService service;

    @Test
    void create_savesAlertWithOpenStatus() {
        AlertDto input = AlertDto.builder().patientId("P001").priority("URGENT")
            .title("High Risk").description("eGFR low").build();
        when(repo.save(any())).thenAnswer(inv -> {
            Alert a = inv.getArgument(0);
            a.setStatus("OPEN");
            return a;
        });

        AlertDto result = service.create(input);
        assertEquals("P001", result.getPatientId());
        assertEquals("OPEN", result.getStatus());
        verify(repo).save(any());
    }

    @Test
    void getOpen_returnsOnlyOpenAlerts() {
        Alert a = Alert.builder().id("A1").patientId("P001").priority("CRITICAL")
            .title("High Risk").status("OPEN").build();
        when(repo.findByStatusOrderByCreatedAtDesc("OPEN")).thenReturn(List.of(a));

        List<AlertDto> results = service.getOpen();
        assertEquals(1, results.size());
        assertEquals("CRITICAL", results.get(0).getPriority());
    }
}
