import re

from System.Collections.Specialized import *
from System.IO import *
from System.Text import *

from Deadline.Scripting import *

from System.IO import File
from DeadlineUI.Controls.Scripting.DeadlineScriptDialog import DeadlineScriptDialog

########################################################################
## Globals
########################################################################
scriptDialog = None
settings = None

########################################################################
## Main Function Called By Deadline
########################################################################
def __main__():
    global scriptDialog
    global settings

    scriptDialog = DeadlineScriptDialog()
        
    selectedJobs = MonitorUtils.GetSelectedJobs()
    if len(selectedJobs) > 1:
        scriptDialog.ShowMessageBox( "Only one job can be selected at a time.", "Multiple Jobs Selected" )
        return

    job = selectedJobs[0]


    outputFilename = job.JobOutputFileNames
    outputDirectory = job.JobOutputDirectories
    outputFilenameSelect = re.sub('[#]', '0', outputFilename[0])
    outputFilenameSelectRennomerMp4 = re.sub('png', 'mov', outputFilenameSelect)

    transferJobID = job.JobId
    transferJobName = job.JobName
    transferFichers = outputDirectory[0]+"/"+outputFilenameSelect
    sortieFichers = outputDirectory[0]+"/"+outputFilenameSelectRennomerMp4
    frameList = job.JobFrames
    chunkSize = job.JobFramesPerTask
    argumentsLine = "-vcodec qtrle -r 25"
    
    #These dont matter. The grid will make the dialog and tab control big enough
    tabWidth = 0
    tabHeight = 0
    
    scriptDialog = DeadlineScriptDialog()
    scriptDialog.SetTitle( "Submit FFmpeg Job To Deadline Custom" )
    scriptDialog.SetIcon( Path.Combine( RepositoryUtils.GetRootDirectory(), "plugins/FFmpeg/FFmpeg.ico" ) )
    
    scriptDialog.AddTabControl("Job Options Tabs", tabWidth, tabHeight)
    scriptDialog.AddTabPage("Job Options")
    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid( "Separator1", "SeparatorControl", "Job Description", 0, 0 )
    scriptDialog.EndGrid()
    
    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid( "NameLabel", "LabelControl", "Job Name", 0, 0, "The name of your job. This is optional, and if left blank, it will default to 'Untitled'.", False )
    scriptDialog.AddControlToGrid( "NameBox", "TextControl", transferJobName+"_Encodage", 0, 1 )

    scriptDialog.AddControlToGrid( "CommentLabel", "LabelControl", "Comment", 1, 0, "A simple description of your job. This is optional and can be left blank.", False )
    scriptDialog.AddControlToGrid( "CommentBox", "TextControl", "", 1, 1 )

    scriptDialog.AddControlToGrid( "DepartmentLabel", "LabelControl", "Department", 2, 0, "The department you belong to. This is optional and can be left blank.", False )
    scriptDialog.AddControlToGrid( "DepartmentBox", "TextControl", "", 2, 1 )
    scriptDialog.EndGrid()

    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid( "Separator2", "SeparatorControl", "Job Options", 0, 0 )
    scriptDialog.EndGrid()
    
    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid( "PoolLabel", "LabelControl", "Pool", 0, 0, "The pool that your job will be submitted to.", False )
    scriptDialog.AddControlToGrid( "PoolBox", "PoolComboControl", "none", 0, 1 )

    scriptDialog.AddControlToGrid( "SecondaryPoolLabel", "LabelControl", "Secondary Pool", 1, 0, "The secondary pool lets you specify a Pool to use if the primary Pool does not have any available Slaves.", False )
    scriptDialog.AddControlToGrid( "SecondaryPoolBox", "SecondaryPoolComboControl", "", 1, 1 )

    scriptDialog.AddControlToGrid( "GroupLabel", "LabelControl", "Group", 2, 0, "The group that your job will be submitted to.", False )
    scriptDialog.AddControlToGrid( "GroupBox", "GroupComboControl", "none", 2, 1 )

    scriptDialog.AddControlToGrid( "PriorityLabel", "LabelControl", "Priority", 3, 0, "A job can have a numeric priority ranging from 0 to 100, where 0 is the lowest priority and 100 is the highest priority.", False )
    scriptDialog.AddRangeControlToGrid( "PriorityBox", "RangeControl", RepositoryUtils.GetMaximumPriority() / 2, 0, RepositoryUtils.GetMaximumPriority(), 0, 1, 3, 1 )

    scriptDialog.AddControlToGrid( "TaskTimeoutLabel", "LabelControl", "Task Timeout", 4, 0, "The number of minutes a slave has to render a task for this job before it requeues it. Specify 0 for no limit.", False )
    scriptDialog.AddRangeControlToGrid( "TaskTimeoutBox", "RangeControl", 0, 0, 1000000, 0, 1, 4, 1 )
    scriptDialog.AddSelectionControlToGrid( "AutoTimeoutBox", "CheckBoxControl", False, "Enable Auto Task Timeout", 4, 2, "If the Auto Task Timeout is properly configured in the Repository Options, then enabling this will allow a task timeout to be automatically calculated based on the render times of previous frames for the job. ", False )

    scriptDialog.AddControlToGrid( "ConcurrentTasksLabel", "LabelControl", "Concurrent Tasks", 5, 0, "The number of tasks that can render concurrently on a single slave. This is useful if the rendering application only uses one thread to render and your slaves have multiple CPUs.", False )
    scriptDialog.AddRangeControlToGrid( "ConcurrentTasksBox", "RangeControl", 1, 1, 16, 0, 1, 5, 1 )
    scriptDialog.AddSelectionControlToGrid( "LimitConcurrentTasksBox", "CheckBoxControl", True, "Limit Tasks To Slave's Task Limit", 5, 2, "If you limit the tasks to a slave's task limit, then by default, the slave won't dequeue more tasks then it has CPUs. This task limit can be overridden for individual slaves by an administrator." )

    scriptDialog.AddControlToGrid( "MachineLimitLabel", "LabelControl", "Machine Limit", 6, 0, "Use the Machine Limit to specify the maximum number of machines that can render your job at one time. Specify 0 for no limit.", False )
    scriptDialog.AddRangeControlToGrid( "MachineLimitBox", "RangeControl", 0, 0, 1000000, 0, 1, 6, 1 )
    scriptDialog.AddSelectionControlToGrid( "IsBlacklistBox", "CheckBoxControl", False, "Machine List Is A Blacklist", 6, 2, "You can force the job to render on specific machines by using a whitelist, or you can avoid specific machines by using a blacklist." )

    scriptDialog.AddControlToGrid( "MachineListLabel", "LabelControl", "Machine List", 7, 0, "The whitelisted or blacklisted list of machines.", False )
    scriptDialog.AddControlToGrid( "MachineListBox", "MachineListControl", "", 7, 1, colSpan=2 )

    scriptDialog.AddControlToGrid( "LimitGroupLabel", "LabelControl", "Limits", 8, 0, "The Limits that your job requires.", False )
    scriptDialog.AddControlToGrid( "LimitGroupBox", "LimitGroupControl", "", 8, 1, colSpan=2 )

    scriptDialog.AddControlToGrid( "DependencyLabel", "LabelControl", "Dependencies", 9, 0, "Specify existing jobs that this job will be dependent on. This job will not start until the specified dependencies finish rendering.", False )
    scriptDialog.AddControlToGrid( "DependencyBox", "DependencyControl", transferJobID, 9, 1, colSpan=2 )

    scriptDialog.AddControlToGrid( "OnJobCompleteLabel", "LabelControl", "On Job Complete", 10, 0, "If desired, you can automatically archive or delete the job when it completes.", False )
    scriptDialog.AddControlToGrid( "OnJobCompleteBox", "OnJobCompleteControl", "Nothing", 10, 1 )
    scriptDialog.AddSelectionControlToGrid( "SubmitSuspendedBox", "CheckBoxControl", False, "Submit Job As Suspended", 10, 2, "If enabled, the job will submit in the suspended state. This is useful if you don't want the job to start rendering right away. Just resume it from the Monitor when you want it to render." )
    scriptDialog.EndGrid()
    
    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid( "Separator3", "SeparatorControl", "FFmpeg Options", 0, 0, colSpan=2 )



    scriptDialog.AddControlToGrid( "Input0Label", "LabelControl", "Input File", 1, 0, "The input file to process.", False )

    scriptDialog.AddSelectionControlToGrid( "Input0Box", "FileBrowserControl", transferFichers, "All Files (*);", 1, 1 )


    scriptDialog.AddControlToGrid( "Input0ArgsLabel", "LabelControl", "Input Arguments", 2, 0, "Additional command line arguments for the input file. ", False )
    scriptDialog.AddControlToGrid( "Input0ArgsBox", "TextControl", "", 2, 1 )



    scriptDialog.AddSelectionControlToGrid( "ReplacePaddingBox", "CheckBoxControl", True, "Replace Frame in Input File(s) With Padding (file%03d.ext)", 3, 1, "If enabled, the frame number in the file name will be replaced by frame padding before being passed to FFMpeg. This should be enabled if you are passing a sequence of images as input." )

    scriptDialog.AddControlToGrid("OutputLabel","LabelControl","Output File", 4, 0, "The output file path.", False)
    scriptDialog.AddSelectionControlToGrid("OutputBox","FileSaverControl",sortieFichers, "MOV Files (*.mov);", 4, 1 )



    scriptDialog.AddControlToGrid( "OutputArgsLabel", "LabelControl", "Output Arguments", 5, 0, "Additional command line arguments for the output file. ", False )
    scriptDialog.AddComboControlToGrid( "CodecControl", "ComboControl", "QuicktimeAnim", ("QuicktimeAnim","Quicktime422","Quicktime422LT","Quicktime422TrameSup","QuicktimeH264","HAP","HAPQ","QuicktimeAnimHorizonInverted"), 5, 1 )

 #   scriptDialog.AddControlToGrid( "OutputArgsBox", "TextControl", argumentsLine, 5, 2 )

    scriptDialog.AddControlToGrid( "AdditionalArgsLabel", "LabelControl", "Additional Arguments", 6, 0, "Additional general command line arguments.", False )
    scriptDialog.AddControlToGrid( "AdditionalArgsBox", "TextControl", "", 6, 1 )

    scriptDialog.AddControlToGrid("PisteAudio","LabelControl","Piste Audio", 7, 0, "The output file path.", False)
    scriptDialog.AddSelectionControlToGrid("AudioBox","FileBrowserControl","", "MP3 Files (*.mp3);WAV Files (*.wav);", 7, 1 )

    scriptDialog.AddSelectionControlToGrid( "overidePng", "CheckBoxControl", False, "Force le rendu sans png...", 8, 1, "A vos risques et périls..." )


    scriptDialog.EndGrid()
    scriptDialog.EndTabPage()
    
    scriptDialog.AddTabPage("Additional Input Files")
    
    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid( "Separator4", "SeparatorControl", "Additional Input Files", 0, 0, colSpan=2 )
    
    scriptDialog.AddSelectionControlToGrid( "UseSameArgsBox", "CheckBoxControl", False, "All Inputs Use Same Arguments as Input 1", 1, 0, "If enabled, all additional input files will use the same arguments as the main input file.", False )
    scriptDialog.EndGrid()
    
    scriptDialog.AddGrid()
    currRow = 0
    for i in range(1,9):
        scriptDialog.AddControlToGrid( "Input%dLabel" % i, "LabelControl", "Input File %d" % (i + 1), currRow, 0, "An additional input file to process.", False )
        scriptDialog.AddSelectionControlToGrid( "Input%dBox" % i, "FileBrowserControl", "", "AVI Files (*.avi);;M2V Files (*.m2v);;MPG Files (*.mpg);;VOB Files (*.vob);;WAV Files (*.wav);;All Files (*)", currRow, 1 )
        currRow += 1
        
        scriptDialog.AddControlToGrid( "Input%dArgsLabel" % i, "LabelControl", "Input Arguments %d" % (i + 1), currRow, 0, "Additional command line arguments for the input file above.", False )
        scriptDialog.AddControlToGrid( "Input%dArgsBox" % i, "TextControl", "", currRow, 1 )
        currRow += 1
    
    scriptDialog.EndGrid()
    scriptDialog.EndTabPage()
    
    scriptDialog.AddTabPage("FFmpeg Preset Files")
    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid( "Separator5", "SeparatorControl", "FFmpeg Preset Files", 0, 0, colSpan=2 )

    scriptDialog.AddControlToGrid( "VideoPresetLabel", "LabelControl", "Video Preset File", 1, 0, "The video preset file.", False )
    scriptDialog.AddSelectionControlToGrid( "VideoPresetBox", "FileBrowserControl", "", "FFmpeg Preset (*.ffpreset);;All Files (*)", 1, 1 )

    scriptDialog.AddControlToGrid( "AudioPresetLabel", "LabelControl", "Audio Preset File", 2, 0, "The audio preset file.", False )
    scriptDialog.AddSelectionControlToGrid( "AudioPresetBox", "FileBrowserControl", "", "FFmpeg Preset (*.ffpreset);;All Files (*)", 2, 1 )

    scriptDialog.AddControlToGrid( "SubtitlePresetLabel", "LabelControl", "Subtitle Preset File", 3, 0, "The subtitle preset file.", False )
    scriptDialog.AddSelectionControlToGrid( "SubtitlePresetBox", "FileBrowserControl", "", "FFmpeg Preset (*.ffpreset);;All Files (*)", 3, 1 )
    scriptDialog.EndGrid()
    scriptDialog.EndTabPage()
    
    scriptDialog.EndTabControl()
    
    scriptDialog.AddGrid()
    scriptDialog.AddHorizontalSpacerToGrid( "HSpacer1", 0, 0 )
    submitButton = scriptDialog.AddControlToGrid( "SubmitButton", "ButtonControl", "Submit", 0, 1, expand=False )
    submitButton.ValueModified.connect(SubmitButtonPressed)
    closeButton = scriptDialog.AddControlToGrid( "CloseButton", "ButtonControl", "Close", 0, 2, expand=False )
    closeButton.ValueModified.connect(scriptDialog.closeEvent)
    scriptDialog.EndGrid()
    
    #Application Box must be listed before version box or else the application changed event will change the version
    settings = ("DepartmentBox","CategoryBox","PoolBox","SecondaryPoolBox","GroupBox","PriorityBox","MachineLimitBox","IsBlacklistBox","MachineListBox","LimitGroupBox","SceneBox","FramesBox","ChunkSizeBox", "ReplacePaddingBox")
    scriptDialog.LoadSettings( GetSettingsFilename(), settings )
    scriptDialog.EnabledStickySaving( settings, GetSettingsFilename() )
    
    scriptDialog.ShowDialog( False )
    
def GetSettingsFilename():
    return Path.Combine( GetDeadlineSettingsPath(), "FFmpegSettings.ini" )
    
def SubmitButtonPressed(*args):
    global scriptDialog
    
    # Check if input files exist.
    inputFile = scriptDialog.GetValue( "Input0Box" )
    
    if( inputFile == "" ):
        scriptDialog.ShowMessageBox( "No input file specified", "Error" )
        return
    

    overidePng = scriptDialog.GetValue( "overidePng" )

    for i in range(0,9):
        inputFile = scriptDialog.GetValue( "Input%dBox" % i ).strip()
        
        if( inputFile != "" and overidePng != True):
            if( not File.Exists( inputFile ) and inputFile.find("%") < 0):
                scriptDialog.ShowMessageBox( "Input file #%d \"%s\" does not exist" % (i, inputFile), "Error" )
                return
            elif (PathUtils.IsPathLocal(inputFile)):
                result = scriptDialog.ShowMessageBox( "Input file %s is local.  Are you sure you want to continue?" % inputFile, "Warning", ("Yes","No") )
                if(result=="No"):
                    return
    
    inputFile = scriptDialog.GetValue( "Input0Box" )
    
    # Check output file.
    outputFile = (scriptDialog.GetValue( "OutputBox" )).strip()
    
    if( outputFile == "" ):
        scriptDialog.ShowMessageBox( "No output file specified", "Error" )
        return
    else:
        if( PathUtils.IsPathLocal( outputFile ) ):
            result = scriptDialog.ShowMessageBox( "Output file %s is local, are you sure you want to continue?" % outputFile, "Warning", ("Yes","No") )
            if( result == "No" ):
                return
    
    # Check video preset file
    vpreFile = (scriptDialog.GetValue( "VideoPresetBox" )).strip()
    
    if( vpreFile != "" ):
        if( not File.Exists( vpreFile ) ):
            scriptDialog.ShowMessageBox( "Video preset file \"%s\" does not exist" % vpreFile, "Error" )
            return
        elif (PathUtils.IsPathLocal(vpreFile)):
            result = scriptDialog.ShowMessageBox( "Video preset file %s is local.  Are you sure you want to continue?" % vpreFile, "Warning", ("Yes","No") )
            if(result=="No"):
                return
    
    # Check audio preset file
    apreFile = (scriptDialog.GetValue( "AudioPresetBox" )).strip()
    
    if( apreFile != "" ):
        if( not File.Exists( apreFile ) ):
            scriptDialog.ShowMessageBox( "Audio preset file \"%s\" does not exist" % apreFile, "Error" )
            return
        elif (PathUtils.IsPathLocal(apreFile)):
            result = scriptDialog.ShowMessageBox( "Audio preset file %s is local.  Are you sure you want to continue?" % apreFile, "Warning", ("Yes","No") )
            if(result=="No"):
                return
    
    # Check subtitle preset file
    spreFile = (scriptDialog.GetValue( "SubtitlePresetBox" )).strip()
    
    if( spreFile != "" ):
        if( not File.Exists( spreFile ) ):
            scriptDialog.ShowMessageBox( "Subtitle preset file \"%s\" does not exist" % spreFile, "Error" )
            return
        elif ( PathUtils.IsPathLocal( spreFile ) ):
            result = scriptDialog.ShowMessageBox( "Subtitle preset file %s is local.  Are you sure you want to continue?" % spreFile, "Warning", ("Yes","No") )
            if( result=="No" ):
                return
    
    # Submit each scene file separately.
    # Create job info file.
    jobInfoFilename = Path.Combine( GetDeadlineTempPath(), "ffmpeg_job_info.job" )
    writer = StreamWriter( jobInfoFilename, False, Encoding.Unicode )
    writer.WriteLine( "Plugin=FFmpeg" )
    writer.WriteLine( "Name=%s" % scriptDialog.GetValue( "NameBox" ) )
    writer.WriteLine( "Comment=%s" % scriptDialog.GetValue( "CommentBox" ) )
    writer.WriteLine( "Department=%s" % scriptDialog.GetValue( "DepartmentBox" ) )
    writer.WriteLine( "Pool=%s" % scriptDialog.GetValue( "PoolBox" ) )
    writer.WriteLine( "SecondaryPool=%s" % scriptDialog.GetValue( "SecondaryPoolBox" ) )
    writer.WriteLine( "Group=%s" % scriptDialog.GetValue( "GroupBox" ) )
    writer.WriteLine( "Priority=%s" % scriptDialog.GetValue( "PriorityBox" ) )
    writer.WriteLine( "TaskTimeoutMinutes=%s" % scriptDialog.GetValue( "TaskTimeoutBox" ) )
    writer.WriteLine( "EnableAutoTimeout=%s" % scriptDialog.GetValue( "AutoTimeoutBox" ) )
    writer.WriteLine( "ConcurrentTasks=%s" % scriptDialog.GetValue( "ConcurrentTasksBox" ) )
    writer.WriteLine( "LimitConcurrentTasksToNumberOfCpus=%s" % scriptDialog.GetValue( "LimitConcurrentTasksBox" ) )
    
    writer.WriteLine( "MachineLimit=%s" % scriptDialog.GetValue( "MachineLimitBox" ) )
    if( bool(scriptDialog.GetValue( "IsBlacklistBox" )) ):
        writer.WriteLine( "Blacklist=%s" % scriptDialog.GetValue( "MachineListBox" ) )
    else:
        writer.WriteLine( "Whitelist=%s" % scriptDialog.GetValue( "MachineListBox" ) )
    
    writer.WriteLine( "LimitGroups=%s" % scriptDialog.GetValue( "LimitGroupBox" ) )
    writer.WriteLine( "JobDependencies=%s" % scriptDialog.GetValue( "DependencyBox" ) )
    writer.WriteLine( "OnJobComplete=%s" % scriptDialog.GetValue( "OnJobCompleteBox" ) )
    
    if( bool(scriptDialog.GetValue( "SubmitSuspendedBox" )) ):
        writer.WriteLine( "InitialStatus=Suspended" )
    
    writer.WriteLine( "Frames=0" ) #%s" % frames )
    writer.WriteLine( "ChunkSize=1" ) #%s" % scriptDialog.GetValue( "ChunkSizeBox" ) )
    writer.WriteLine( "OutputFilename0=%s" % outputFile )
    
    writer.Close()
    
    # Create plugin info file.
    pluginInfoFilename = Path.Combine( GetDeadlineTempPath(), "ffmpeg_plugin_info.job" )
    writer = StreamWriter( pluginInfoFilename, False, Encoding.Unicode )


    # Code maison Clément !!
    codecChoisi = scriptDialog.GetValue( "CodecControl" ).strip()
    if codecChoisi=="QuicktimeAnim":
        argumentFFmpeg = "-vcodec qtrle -r 25" 
    elif codecChoisi=="Quicktime422":
        argumentFFmpeg = "-c:v prores -f mov -metadata:s encoder=\"Apple ProRes 422\" -top -1 -profile:v 2 -vendor ap10" 
    elif codecChoisi=="Quicktime422LT":
        argumentFFmpeg = "-c:v prores -f mov -metadata:s encoder=\"Apple ProRes 422 LT\" -top -1 -profile:v 1 -vendor ap10" 
    elif codecChoisi=="QuicktimeH264":
        argumentFFmpeg = "-c:v libx264 -b:v 30000k -pix_fmt yuv420p"
    elif codecChoisi=="Quicktime422TrameSup":
        argumentFFmpeg = "-c:v prores_ks -f mov -metadata:s encoder=\"Apple ProRes 422\" -top 1 -flags ildct+ilme -profile:v standard -vf \"setfield=1, fieldorder=bff\" -vendor ap10 -bsf:a aac_adtstoasc" 
    elif codecChoisi=="HAP":
        argumentFFmpeg = "-vcodec hap -format hap" 
    elif codecChoisi=="HAPQ":
        argumentFFmpeg = "-vcodec hap -format hap_q" 
    elif codecChoisi=="QuicktimeAnimHorizonInverted":
        argumentFFmpeg = "-vcodec qtrle -r 25 -vf \"hflip\"" 

    
    for i in range(0,9):
        writer.WriteLine("InputFile%d=%s" % (i, scriptDialog.GetValue( "Input%dBox" % i ).strip()) )
        writer.WriteLine("InputArgs%d=%s" % (i, scriptDialog.GetValue( "Input%dArgsBox" % i ).strip()))
    
    writer.WriteLine( "ReplacePadding=%s" % scriptDialog.GetValue( "ReplacePaddingBox" ) )
    writer.WriteLine( "OutputFile=%s" % outputFile )
    if (scriptDialog.GetValue( "AudioBox" ).strip() == ""):
        writer.WriteLine( "OutputArgs=%s" % argumentFFmpeg )
    else:
        writer.WriteLine( "OutputArgs=%s" % ' -i "'+scriptDialog.GetValue( "AudioBox" ).strip()+'" '+argumentFFmpeg )
    
    writer.WriteLine( "UseSameInputArgs=%s" % scriptDialog.GetValue( "UseSameArgsBox" ) )
    writer.WriteLine( "AdditionalArgs=%s" % scriptDialog.GetValue( "AdditionalArgsBox" ) )
    writer.WriteLine( "VideoPreset=%s" % scriptDialog.GetValue( "VideoPresetBox" ) )
    writer.WriteLine( "AudioPreset=%s" % scriptDialog.GetValue( "AudioPresetBox" ) )
    writer.WriteLine( "SubtitlePreset=%s" % scriptDialog.GetValue( "SubtitlePresetBox" ) )
    
    writer.Close()
    
    # Setup the command line arguments.
    arguments = StringCollection()
    
    arguments.Add( jobInfoFilename )
    arguments.Add( pluginInfoFilename )
    
    # Now submit the job.
    results = ClientUtils.ExecuteCommandAndGetOutput( arguments )
    scriptDialog.ShowMessageBox( results, "Submission Results" )
