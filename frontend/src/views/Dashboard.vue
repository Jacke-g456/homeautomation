<template>
    <VContainer>
            <!-- ROW 1 -->
        <v-row class="row" justify="center" align="center">
            <!-- COLUMN 1 -->
            <v-col align="left">
                <v-sheet class="sheet" width="100">
                    <v-card flat>
                        <v-slider color="green" v-model="radarValue" max="100" thumb-label direction="vertical" track-size="60" label="Height(in)"></v-slider>
                    </v-card>
                </v-sheet>
            </v-col>
            <!-- COLUMN 2 -->
            <v-col class="column bg-surface" cols="10" align="left">
                <v-sheet class="sheet" border max="100">
                    <v-card>
                        <figure class="highcharts-figure">
                            <div id="container"></div>
                        </figure>
                    </v-card>   
                </v-sheet>
            </v-col>
        </v-row>

        <!-- ROW 2 -->
        <v-row>
            <!-- COLUMN 1 -->
            <v-col class="column" cols="8" align="right">
                <v-sheet class="sheet0" border max="400">
                    <v-card flat>
                        <figure class="highcharts-figure">
                            <div id="container1"></div>
                        </figure>
                    </v-card>   
                </v-sheet>
            </v-col>
            <!-- COLUMN 2 -->
            <v-col class="column" cols="4">
                <v-card class="text-secondary" title="Water Level" subtitle="Capacity Remaining"  flat variant="tonal">
                    <div id="fluid-meter"></div>
                </v-card>   
            </v-col>
        </v-row>

        <v-dialog v-model="overflowDialog" max-width="400">
            <template v-slot:default="{ overflowDialog }">
                <v-card title="Overflow Detected" color="warning" background-color="primary darken-1">
                    <v-card-actions>
                        <v-spacer></v-spacer>
                    </v-card-actions>
                </v-card>
            </template>
        </v-dialog>
        
    
    
    </VContainer>
</template>

<script setup>
/** JAVASCRIPT HERE */

// IMPORTS
import { ref,reactive,watch ,onMounted,onBeforeUnmount,computed } from "vue";  
import { useRoute ,useRouter } from "vue-router";

import { useAppStore } from "@/store/appStore";
import { useMqttStore } from "@/store/mqttStore"; // Import Mqtt Store
import { storeToRefs } from "pinia";

 
import Highcharts from 'highcharts'; 
import more from 'highcharts/highcharts-more'; 
import Exporting from 'highcharts/modules/exporting'; 
Exporting(Highcharts);  
more(Highcharts);
 
 
// VARIABLES
const router      = useRouter();
const route       = useRoute();  
const Mqtt = useMqttStore();

const AppStore    = useAppStore();
const { payload, payloadTopic } = storeToRefs(Mqtt);


const waterReserveChart = ref(null);
const waterGaugeChart = ref(null);
const points       = ref(10);
const shift       = ref(false);
const radar_val = ref(null);
const overflow      = ref(false);
var fluid_meter = new FluidMeter();

const waterheight= computed(()=>{
    if(!!payload.value){
      return `${payload.value.waterheight.toFixed(2)} inches`;
    }
    }
  );

  const reserve= computed(()=>{
    if(!!payload.value){
      return `${payload.value.reserve.toFixed(2)} gallons`;
    }
    }
  );

const percentage= computed(()=>{
    if(!!payload.value){
      return `${payload.value.percentage.toFixed(2)}`;
    }
    }
);

// FUNCTIONS
onMounted(()=>{
    // THIS FUNCTION IS CALLED AFTER THIS COMPONENT HAS BEEN MOUNTED
    Mqtt.connect(); // Connect to Broker located on the backend
    setTimeout( ()=>{
        // Subscribe to each topic
        Mqtt.subscribe("620165845");
        Mqtt.subscribe("620165845_pub");
    },3000)
});


onBeforeUnmount(()=>{
    // THIS FUNCTION IS CALLED RIGHT BEFORE THIS COMPONENT IS UNMOUNTED
    Mqtt.unsubcribeAll();
});

const CreateCharts = async () => {
// waterReserveChart
    waterReserveChart = Highcharts.chart('container', {
        chart: { zoomType: 'x' },
        title: { text: 'Water Reserves(10 min)', align: 'left' },
        yAxis: {
            title: { text: 'Water level' , style:{color:'#000000'}},
            labels: { format: '{value} Gal' }
        },
        xAxis: {
            type: 'datetime',
            title: { text: 'Time', style:{color:'#000000'} },
        },
        tooltip: { shared:true, },
        series: [
            {
                name: 'Water',
                type: 'area',
                data: [],
                turboThreshold: 0,
                color: Highcharts.getOptions().colors[0]
            },],
    });

     // waterGaugeChart 
    waterGaugeChart.value = Highcharts.chart('container1', {
        chart: { zoomType: 'x' },
        title: { text: 'Water Reserves', align: 'left' },
        yAxis: {
            min: 0,
            max: 1000,
            tickPixelInterval: 72,
            tickPosition: 'inside',
            tickColor:  Highcharts.defaultOptions.backgroundColor || '#FFFFFF',
            tickLength: 20,
            tickWidth: 2,
            minorTickInterval: null,
            labels: {distance: 20, style: {fontSize: '14px'}},
            lineWidth: 0,
            plotBands: [
                {
                    from: 0,
                    to: 200,
                    color: '#DF5353',
                    thickness: 20
                },
                {
                    from: 200,
                    to: 600,
                    color: '#DDDF0D',
                    thickness: 20
                },
                {
                    from: 600,
                    to: 1000,
                    color: '#55BF3B',
                    thickness: 20
                }
            ]
        },
        tooltip: { shared:true, },
        pane: {
            startAngle: -90,
            endAngle: 89.9,
            background: null,
            center: ['50%', '75%'],
            size: '110%'
        },
        series: [
            {
                name: 'Water Capacity',
                type: 'gauge',
                data: [0],
                dataLabels: {
                    format: '{y} Gal',
                    borderWidth: 0,
                    color: (Highcharts.defaultOptions.title && Highcharts.defaultOptions.title.style && Highcharts.defaultOptions.title.style.color) || '#333333',
                    style: { fontSize: '16px'},
                    dial: {
                        radius: '80%',
                        backgroundColor: 'gray',
                        baseWidth: 12,
                        baseLength: '0%',
                        rearLength: '0%'
                    },
                    pivot: {backgroundColor: 'gray', radius: 6
                    }
                },
                
                turboThreshold: 0,
                color: Highcharts.getOptions().colors[1]
            } ],
    });
    fluid_meter.init({
    targetContainer: document.getElementById("fluid-meter"),
    fillPercentage: 15,
    options: {
        fontSize: '70px',
        fontFamily: "Arial",
        fontFillStyle: "white",
        drawShadow: true,
        drawText: true,
        drawPercentageSign: true,
        size: 300,
        borderWidth: 25,
        
    }
})
};

watch(payload, (data) => {
    // THIS FUNCTION IS CALLED WHEN THE VALUE OF THE VARIABLE "payload" CHANGES
    
    if(waterReserveChart.value.series[0].points.value > 550){ 
        waterReserveChart.value.series[0].points.value -- ; }
        else{ shift.value = true; }
    
    radar_val.value = data.radar
    
    if (data.waterheight >= 77) {
      fluid_meter.setPercentage(100);
     
      waterReserveChart.value.series[0].addPoint({ y: parseFloat(data.waterheight.toFixed(2)), x: data.timestamp*1000 }, true, shift.value); // Add new data point
      waterGaugeChart.value.series[0].points[0].update(1000); // Add new data point
    }
    else if (data.waterheight <= 0) {
      fluid_meter.setPercentage(0);
      waterReserveChart.value.series[0].addPoint({ y: 0, x: data.timestamp*1000 }, true, shift.value); // Add new data point
      waterGaugeChart.value.series[0].points[0].update(0); // Add new data point

    }
    else{
      fluid_meter.setPercentage(data.percentage.toFixed(2));
      waterReserveChart.value.series[0].addPoint({ y: parseFloat(data.waterheight.toFixed(2)), x: data.timestamp*1000  }, true, shift.value); // Add new data point
      waterGaugeChart.value.series[0].points[0].update(parseFloat(data.reserve.toFixed(2)));}    

      console.log(data.percentage);
      if (data.percentage >=100 || data.percentage < 2) {
        overflow.value = true;
        } else {
            overflow.value = false;
        }
});

</script>


<style scoped>
/** CSS STYLE HERE */


</style>
  