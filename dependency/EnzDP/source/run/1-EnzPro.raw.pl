#! perl -w

### INPUT ###
$fastaFile = $ARGV[0];
$SGRDir	= "../../data";
$sgrListFile = "$SGRDir/SGR.list";
$hmmDir = "../../HMMs/";

$tmpDir	= $ARGV[1];
mkdir($tmpDir);

### OUTPUT ###
$outFile 	= $ARGV[2];

$siteFileFinal 	= $ARGV[3]; 
$siteFile 		= $siteFileFinal. ".tmp";
#=======================================
# Load the sgr list:
@SGRList = ();
open(FILE,$sgrListFile)||die ($sgrListFile);
while(<FILE>){
	($sgr) = split(/\s+/,$_);
	push(@SGRList,$sgr);	
}
close(FILE);

#=======================================
# query profiles of each sgr to the fasta file:
$total = $#SGRList +1;
$cnt = 0;
$startTime = time;

#open(OUTPUT	,">",$outFile	);	# write output to this file
#unlink($siteFile);
print "\tcalculating raw result...\n";
foreach $sgr (@SGRList){
	$Elapsed = time - $startTime;
	$cnt++;

#	$pm->start and next;

	print "\t[$cnt/$total] run for $sgr:  [$Elapsed seconds]:              \n" if ($cnt % 100 == 0);
	my $hmmFile = $hmmDir ."$sgr.hmm";
	if (!(-e $hmmFile)){
#		$pm->finish;	
		next;
	};
	my $search_out = "$tmpDir/$sgr.search_out";
	unlink($search_out);
	system("perl searchHMM.pl $hmmFile $fastaFile $search_out"); 
	my $alignment	= "$search_out.raw";
	my $siteOut	= "$alignment.sites";
	unlink($siteOut);
	system("perl findSites.pl	$alignment	$siteOut");

#	$pm->finish;
}
#$pm->wait_all_children;
#for each sgr
print "\n\tdone.\n";

#print "Writing raw result into files [$outFile] and [$siteFile]:\n";

print "\twriting...";
open(OUTPUT, ">",$outFile);
unlink($siteFile);

foreach $sgr (@SGRList){
	# hit domain
	$search_out = "$tmpDir/$sgr.search_out";	
	next if (! -e $search_out);
	open(FILE,$search_out);
	while(<FILE>){
		next if (/^>/);
		print OUTPUT $sgr ."\t". $_;
	};
	close(FILE);
	# hit specific sites:
	$alignment	= "$search_out.raw";
	$siteOut	= "$alignment.sites";
	next if (! -e $siteOut);
	system("cat $siteOut >> $siteFile");
}; # for each sgr
print " done\n";

#print "Writing raw result into files [$outFile] and [$siteFile]: DONE.\n";

system("sort -k1,1 -k6,6nr $siteFile > $siteFileFinal");
#print "Matched specific sites are stored in [$siteFileFinal]\n";
