# VaspReader
VaspReader is a program for visualisation and processing of the VASP(Vienna ab initio simulation package) results and some other tasks which will be described later.

The program have a wide range of functions for simplify a rootine connected with processing calculation's results. For example, if you have calculation with two or more .xml files you need to spend much time to link a data together and VaspReader can automatically complete this task.

The list of VaspReader functions:
1. Visualisation of calculations. At a visualitation window user can rotate, scale and translate a model (program use 4*4 matrix including 3*3 euler rotation matrix). Here are some additional options of this window that user can change and use:

   1.1. view mode: perspective, orthographic,
   
   1.2. background color,
   
   1.3. light settings,
   
   1.4. drawing of axes (on/off),

   1.5. drawing of a model cell (on/off),

   1.6. drawing of bonds (opening a window with settings connected with a bond lenght, a bond width, the choice of atoms between which bonds should be drawn),

   1.7. selection of atoms for the next processing (only keyboard and mouse+keyboard),

   1.8. drawing labels, bond lenghtes and valence angles for selected atoms,

   1.9. form a POSCAR file for chosen step,

   1.10. do an screenshot,

   1.11. save and load visualisation state.

3. Processing of calculations. After selecting of atoms at visualisation window and choosing processing mode by clicking an option from menu or pressing p button at the keyboard, user moves to processing window where for selected atoms can be calculated:

   2.1. distances between atoms,

   2.2. angles with selected planes or valence angles,

   2.3. energy of center of mass for chosen atoms,

   2.4. summary energy for chosen atoms,

   2.5. energy difference for chosen atoms,

   2.6. rotational and vibrational energy for diatomic molecules.

Also user can include OSZICAR data to table and save resulted tables in .csv and .xslx formats.

3. Plotting. After processing user can plot gained dependences (with ability of including several dependences) and save it at .png, .pdf, .jpg, .tif formats. Also this window provides functions for choose x and y diapasones and change a graph legend and labels.
4. OSZICAR processing.
5. Linking with supercomputer (only for lomonosov-2 supercomputer now). Suggest two options: filesharing and console management, which helps with starting of tasks and sharing of files with supercomputer from VaspReader program. This function is not completed.
6. Raman and IR spectra calculations. This function is not completed.
7. POSCAR visualitation. Draw an POSCAR file chosen from list of files (if it more than one file in directory).

I hope that you will enjoy the expirience of using this program. For any sugestions and bug reports send me a mail to: solovykh.aa19@physics.msu.ru.
