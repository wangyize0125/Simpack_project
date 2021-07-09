function main(){

  // parse arguments and call your worker function
  // do not do anything else in main()
  
  // args is the command line inputs
  // you can use "" to encapsulate your input to include blanks
  if(arguments) {

    var args = String(arguments[0]).split("?");

    if(args.length == 2) {   
      // the first and second args are result filename and output filename
      // open the sbr file
      var proj = Application.Spck.addProject();
      Application.Spck.proj1.addResultFile(args[0]);
      
      // plot the figures
      {{ macro_name }}();

      // export txt file
      Application.AsciiExporter.exportToFile(Application.Spck.proj1, args[1]);
    }   
    else {
      return 1;
    }
  }
  else{
    return 1;
  }
}