package com.healthmap.patient.controller;

import com.healthmap.patient.dto.LabResultDto;
import com.healthmap.patient.service.LabResultService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import java.util.List;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class LabResultControllerTest {

    @Autowired private MockMvc mvc;
    @MockBean private LabResultService service;

    @Test
    void getLabs_returnsResults() throws Exception {
        LabResultDto dto = LabResultDto.builder().labId("L001").patientId("P001")
            .testName("eGFR").value(22.0).unit("mL/min").isAbnormal(true).build();
        when(service.getByPatient("P001", 10)).thenReturn(List.of(dto));

        mvc.perform(get("/api/v1/labs/P001"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.results[0].testName").value("eGFR"))
            .andExpect(jsonPath("$.results[0].value").value(22.0));
    }

    @Test
    void getAbnormal_returnsOnlyAbnormal() throws Exception {
        LabResultDto dto = LabResultDto.builder().labId("L002").testName("Potassium")
            .value(5.8).isAbnormal(true).build();
        when(service.getAbnormalByPatient("P001")).thenReturn(List.of(dto));

        mvc.perform(get("/api/v1/labs/P001/abnormal"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].isAbnormal").value(true));
    }
}
