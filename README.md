# crack_it
A Blender addon to makes a cracked object based on selected object. Also you can use material preset for cracked objects.

## Links
* Blender Artist Thread:
* Turorial:
* Turorial video:
* Example Series: 

## Installation

WARNING1: Please enable 'Object: Cell Fracture' addon before use the addon!!
WARNING2: Obejects which have many vertices or complex shape could take huge amount of time to make crack.
          So I recommend using simple object, or simplifying object by applying decimate modifier in advance.

## Basic Usage
1. Select an object.
2. Find the addon' location in create tab in the toolshelf left. It's usually the same tab of 'Add Primitive'.
3. Click 'Crack It' button. It makes cracked object with some modifiers.
4. Tweak modifier setting. Decimate modifeir to simplify shape, Smooth modifier to smooth shape.
5. Select material preset and click 'Apply Material' button.

## Options
####Crack Option:
'Scale X/Y/Z': Scale of crack's shape. To make long crack like bark of tree, decrease scale of an axis.
'Max Crack': Max number of crack. Notice that if you increase it too much, calculation will take long time.
'Margin Size': Margin of crack. To make more gap of crack, increase it.
'Extrude': Extrusion size along with object's normal.
'Random': Randomness of crack' rotation and scale.

####Material Preset:
'Excrement': Poop/shit material
'Mud': Mud Material
'Tree': Tree Material
'Rock': Rock Material

## Versions
Download: [v0.1.0.zip]()