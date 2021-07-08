//
// Macro recorded on 2021/7/2 13:30
//

function macro ()
{
// Rename Page
Application.Spck.proj1.pset1.page1.title.src = "PitchAngle_Blade1";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page2.title.src = "PitchAngle_Blade2";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page3.title.src = "PitchAngle_Blade3";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page4.title.src = "GeneratorSpeedSensor";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page5.title.src = "DemandGenTorque";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page6.title.src = "Force_Blade1";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page7.title.src = "Force_Blade2";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page8.title.src = "Force_Blade3";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page9.title.src = "Force_TWR";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page10.title.src = "Force_YBR";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page11.title.src = "Torque_Blade1";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page12.title.src = "Torque_Blade2";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page13.title.src = "Torque_Blade3";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page14.title.src = "Torque_TWR";
// start of internal macro "Add Page"
// Create Page
Application.Spck.proj1.pset1.addPage();
// end of internal macro

// Rename Page
Application.Spck.proj1.pset1.page15.title.src = "Torque_YBR";
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page1.addDiagram(0, Application.Spck.proj1.pset1.page1.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.forceOv.C_AppliedPitchAngleBlade1.ov_001);
}
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page2.addDiagram(0, Application.Spck.proj1.pset1.page2.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.forceOv.C_AppliedPitchAngleBlade2.ov_001);
}
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page3.addDiagram(0, Application.Spck.proj1.pset1.page3.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.forceOv.C_AppliedPitchAngleBlade3.ov_001);
}
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page4.addDiagram(0, Application.Spck.proj1.pset1.page4.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.forceOv.C_GeneratorSpeedSensor.ov_001);
}
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page5.addDiagram(0, Application.Spck.proj1.pset1.page5.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.forceOv.C_DemandGenTorque.ov_002);
}
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page6.addDiagram(0, Application.Spck.proj1.pset1.page6.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.jointForce.S_Blade1__J_RBL.x);
}
// Create Curve
Application.Spck.proj1.pset1.page6.diag1.addCurve(Application.Spck.proj1.resf1.jointForce.S_Blade1__J_RBL.y);
// Create Curve
Application.Spck.proj1.pset1.page6.diag1.addCurve(Application.Spck.proj1.resf1.jointForce.S_Blade1__J_RBL.z);
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page7.addDiagram(0, Application.Spck.proj1.pset1.page7.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.jointForce.S_Blade2__J_RBL.x);
}
// Create Curve
Application.Spck.proj1.pset1.page7.diag1.addCurve(Application.Spck.proj1.resf1.jointForce.S_Blade2__J_RBL.y);
// Create Curve
Application.Spck.proj1.pset1.page7.diag1.addCurve(Application.Spck.proj1.resf1.jointForce.S_Blade2__J_RBL.z);
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page8.addDiagram(0, Application.Spck.proj1.pset1.page8.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.jointForce.S_Blade3__J_RBL.x);
}
// Create Curve
Application.Spck.proj1.pset1.page8.diag1.addCurve(Application.Spck.proj1.resf1.jointForce.S_Blade3__J_RBL.y);
// Create Curve
Application.Spck.proj1.pset1.page8.diag1.addCurve(Application.Spck.proj1.resf1.jointForce.S_Blade3__J_RBL.z);
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page9.addDiagram(0, Application.Spck.proj1.pset1.page9.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.jointForce.S_TWR__J_TWR.x);
}
// Create Curve
Application.Spck.proj1.pset1.page9.diag1.addCurve(Application.Spck.proj1.resf1.jointForce.S_TWR__J_TWR.y);
// Create Curve
Application.Spck.proj1.pset1.page9.diag1.addCurve(Application.Spck.proj1.resf1.jointForce.S_TWR__J_TWR.z);
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page10.addDiagram(0, Application.Spck.proj1.pset1.page10.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.jointForce.S_YBR__J_YBR.x);
}
// Create Curve
Application.Spck.proj1.pset1.page10.diag1.addCurve(Application.Spck.proj1.resf1.jointForce.S_YBR__J_YBR.y);
// Create Curve
Application.Spck.proj1.pset1.page10.diag1.addCurve(Application.Spck.proj1.resf1.jointForce.S_YBR__J_YBR.z);
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page11.addDiagram(0, Application.Spck.proj1.pset1.page11.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.jointTorque.S_Blade1__J_RBL.x);
}
// Create Curve
Application.Spck.proj1.pset1.page11.diag1.addCurve(Application.Spck.proj1.resf1.jointTorque.S_Blade1__J_RBL.y);
// Create Curve
Application.Spck.proj1.pset1.page11.diag1.addCurve(Application.Spck.proj1.resf1.jointTorque.S_Blade1__J_RBL.z);
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page12.addDiagram(0, Application.Spck.proj1.pset1.page12.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.jointTorque.S_Blade2__J_RBL.x);
}
// Create Curve
Application.Spck.proj1.pset1.page12.diag1.addCurve(Application.Spck.proj1.resf1.jointTorque.S_Blade2__J_RBL.y);
// Create Curve
Application.Spck.proj1.pset1.page12.diag1.addCurve(Application.Spck.proj1.resf1.jointTorque.S_Blade2__J_RBL.z);
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page13.addDiagram(0, Application.Spck.proj1.pset1.page13.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.jointTorque.S_Blade3__J_RBL.x);
}
// Create Curve
Application.Spck.proj1.pset1.page13.diag1.addCurve(Application.Spck.proj1.resf1.jointTorque.S_Blade3__J_RBL.y);
// Create Curve
Application.Spck.proj1.pset1.page13.diag1.addCurve(Application.Spck.proj1.resf1.jointTorque.S_Blade3__J_RBL.z);
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page14.addDiagram(0, Application.Spck.proj1.pset1.page14.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.jointTorque.S_TWR__J_TWR.x);
}
// Create Curve
Application.Spck.proj1.pset1.page14.diag1.addCurve(Application.Spck.proj1.resf1.jointTorque.S_TWR__J_TWR.y);
// Create Curve
Application.Spck.proj1.pset1.page14.diag1.addCurve(Application.Spck.proj1.resf1.jointTorque.S_TWR__J_TWR.z);
// Create Curve
{
var diag = Application.Spck.proj1.pset1.page15.addDiagram(0, Application.Spck.proj1.pset1.page15.DIAGRAM_2D);
diag.addCurve(Application.Spck.proj1.resf1.jointTorque.S_YBR__J_YBR.x);
}
// Create Curve
Application.Spck.proj1.pset1.page15.diag1.addCurve(Application.Spck.proj1.resf1.jointTorque.S_YBR__J_YBR.y);
// Create Curve
Application.Spck.proj1.pset1.page15.diag1.addCurve(Application.Spck.proj1.resf1.jointTorque.S_YBR__J_YBR.z);
}
