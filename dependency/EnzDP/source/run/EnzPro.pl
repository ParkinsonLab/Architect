#! perl -w 

#=================================================
#
#=================================================

### INPUT ###
#============
$inputFasta 	= $ARGV[0];
$datasetName	= getDatasetName($inputFasta);

$cutThreshold	= $ARGV[1];

$nCPU =0;
$nARGV = $#ARGV + 1;
if ($nARGV>4){
    $nCPU = 0+$ARGV[4];
}

$resDir = "$ARGV[3]/RES";
mkdir($resDir);

$progName = "EnzPro";

### OUTPUT ###
#=============
$outputFile		= $ARGV[2];
$outputFileSite	= "$outputFile.sites";



# Process arguments:
#===================
print "[$progName] Input fasta file is \t[$inputFasta]\n";
die "[$progName] ERROR: File [$inputFasta] does not exist.\n" if (! -e $inputFasta);

print "[$progName] Dataset name is \t[$datasetName]\n";
print "[$progName] Output file will be \t[$outputFile]\n";
print "[$progName] Cut-off threshold is \t[$cutThreshold]\n\n";

die "[$progName] ERROR: Cut-off threshold is expected to be in range [0-1]\n" if (($cutThreshold <0) or ($cutThreshold >1));


# Creating folders:
# =================
$resDir = "$resDir/$datasetName";
mkdir($resDir);
print "[$progName] Created result folder  \t[$resDir]\n";

$tmpResDir = "$resDir/TMP";
mkdir($tmpResDir);
print "[$progName] Created tmp result folder \t[$tmpResDir]\n";

$rawResDir = "$resDir/RAW";
mkdir($rawResDir);
print "[$progName] Created raw result folder \t[$rawResDir]\n\n";

# Running:
#=========
print "[$progName] Calculating raw result...\n";
$rawOutputFile = "$rawResDir/$datasetName.raw";
$siteFinalFile = "$rawResDir/$datasetName.sites";
if ($nCPU==0){
    system("perl 1-EnzPro.raw.pl $inputFasta $tmpResDir $rawOutputFile $siteFinalFile");
} else{
    system("perl 1-EnzPro.raw-t.pl $inputFasta $tmpResDir $rawOutputFile $siteFinalFile $nCPU");
}
print "[$progName] Calculating raw result... DONE\n\n";


print "[$progName] Adding prediction probability...\n";
$addedRawOutputFile = "$rawOutputFile.added";
system("perl 2-EnzPro.add.pl $rawOutputFile $addedRawOutputFile");
print "[$progName] Adding prediction probability... DONE\n\n";


print "[$progName] Filtering prediction result with threshold [$cutThreshold]\n";
$filteredAddedRawOutputFile = "$addedRawOutputFile.filtered";
system("perl 3-EnzPro.filter.pl $addedRawOutputFile  $cutThreshold	$filteredAddedRawOutputFile");
print "[$progName] Filtering prediction result... DONE\n\n";

#Add result format, (modified by NNN Feb-2016):
system("cat res.format > $outputFile");
system("sort -k1,1 -k3,3nr $filteredAddedRawOutputFile >> $outputFile");
system("cat $siteFinalFile > $outputFileSite");
print "[$progName] Writing output file [$outputFile] and [$outputFileSite]: DONE\n\n";

print "Look for result in [$outputFile] and [$outputFileSite]. Bye!\n";

##################################################
##################################################
##################################################

sub getDatasetName{
	my $str = shift;
	local @tmpArr = split(/\//,$str);	
	$str	= $tmpArr[-1];
	#($str)	= split(/\./,$str);
	$str	=~ s/\./_/g;
	return $str;
};
