package com.healthmap.patient.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.healthmap.patient.dto.AlertDto;
import com.healthmap.patient.service.AlertService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import java.util.List;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class AlertControllerTest {

    @Autowired private MockMvc mvc;
    @Autowired private ObjectMapper mapper;
    @MockBean private AlertService service;

    @Test
    void createAlert_returns201() throws Exception {
        AlertDto input = AlertDto.builder().patientId("P001").priority("URGENT")
            .title("High Risk").description("eGFR declining").build();
        AlertDto output = AlertDto.builder().alertId("A001").patientId("P001")
            .priority("URGENT").title("High Risk").status("OPEN").build();
        when(service.create(any())).thenReturn(output);

        mvc.perform(post("/api/v1/alerts")
                .contentType(MediaType.APPLICATION_JSON)
                .content(mapper.writeValueAsString(input)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.alertId").value("A001"))
            .andExpect(jsonPath("$.status").value("OPEN"));
    }

    @Test
    void getOpen_returnsOpenAlerts() throws Exception {
        AlertDto a = AlertDto.builder().alertId("A1").patientId("P001").priority("CRITICAL")
            .title("Risk").status("OPEN").build();
        when(service.getOpen()).thenReturn(List.of(a));

        mvc.perform(get("/api/v1/alerts/open"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].priority").value("CRITICAL"));
    }
}
