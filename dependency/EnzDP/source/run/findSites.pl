#! /usr/bin/perl -w


#===INPUT===#
$hmmSearchOutFile 	= $ARGV[0];

$HMMDir		=	"../../HMMs";

#===OUTPUT===#
$OutFile 	=	$ARGV[1];


#=== Global vars===#
%BestBSOf		= ();

@HMMSites		= ();
%HitCharOfPos	= ();
%HitPosOfPos	= ();

@QueryStarts 	= ();
@QueryStrings 	= ();
@QueryEnds		= ();
@HitStarts 		= ();
@HitStrings 	= ();
@HitEnds		= ();

#print "input 	is $hmmSearchOutFile\n";
#print "output 	is $OutFile\n";

#=================================================
# read search out file
open(FILE,$hmmSearchOutFile) || warn "File $hmmSearchOutFile missing?\n";

$HitStartFlag = 0;
$myHitID = "InitHitIDName";
$AlignmentStartFlag = 0;
$queryName = "ToBeChecked";

open(OUTSITE,">$OutFile");
$lCnt = 0;
$BestDomStartFlag = 0;
while(<FILE>){
	$lCnt++;
	if (/^Query:/){
		(undef,$queryName) = split;
#		print "Query HMM name is $queryName\n";
		readSiteFile($queryName);
		next;
	};

	next if ($lCnt < 16);

	if ($HitStartFlag == 0){
		next if (/inclusion threshold/);
		(undef, undef, undef, undef, $bestBS, undef, undef, undef, $spACID) = split;
		$BestBSOf{$spACID} = $bestBS if ($spACID);
	};

	if (/^Domain annotation for each sequence/){	# Start of hit description
		$HitStartFlag = 1;
		next;
	}
	next if ($HitStartFlag == 0);

	if (/^>>\s/){
		if ($AlignmentStartFlag == 1){ #done last alignment
			#do-some-thing;
#			print "Check site for hit id [$myHitID]:\n";
			checkSites($myHitID) if !($myHitID =~ /InitHitIDName/);
		}	
		(undef,$myHitID) = split;
		$AlignmentStartFlag = 0;

		@QueryStarts 	= ();
		@QueryStrings 	= ();
		@QueryEnds		= ();

		@HitStarts 	= ();
		@HitStrings 	= ();
		@HitEnds		= ();

		$BestDomStartFlag = 0;
		$BestDomID = 0;

		next;
	}; #if (/^>>\s/)

	$AlignmentStartFlag = 1;

	#start reading alignment:

	if (/\!/){
		($domID,undef,$bs) = split;
		$BestDomID = $domID if ($bs == $BestBSOf{$myHitID});
		next;
	};
	
	if (/== domain/){
		$BestDomStartFlag = 0;
		$BestDomStartFlag = 1 if (/== domain\s+\Q$BestDomID\E/);
	};

	next if ($BestDomStartFlag == 0);

	if (/\Q$queryName\E/){
		(undef,$start,$string,$end) = split;
		push(@QueryStarts, $start);		
		push(@QueryStrings, $string);		
		push(@QueryEnds, $end);	
		#print $_;	
	}
	
	if (/\Q$myHitID\E/){
		(undef,$start,$string,$end) = split;
		push(@HitStarts, $start);		
		push(@HitStrings, $string);		
		push(@HitEnds, $end);	
		#print $_;	
	};

};
close(FILE);
close(OUTSITE);
##################################################
##################################################


sub checkSites{
	%HitCharOfPos		= ();	#global, reset
	%HitPosOfPos		= ();	#global, reset
	for($i = 0; $i <=$#QueryStarts; $i++){
		#print $QueryStarts[$i]	."\t".$QueryStrings[$i]	."\t".$QueryEnds[$i]."\n";
		#print $HitStarts[$i]	."\t".$HitStrings[$i]	."\t".$HitEnds[$i]."\n";
#        1.6.99.5.sgr21  12 illlelikGlgitlk.......tllkktvTleYPeekvelppryrGrhaltrredgkerCvaCylCataCPaqciyieaaeekdeagek 93  
#  sp|P0AFD8|NUOI_ECO57   1 MTLKELLVGFGTQVRsiwmiglHAFAKRETRMYPEEPVYLPPRYRGRIVLTRDPDGEERCVACNLCAVACPVGCISLQKAETKD--GRW 87 
		next if ($HitStarts[$i] !~ /\d/);
		$posHit = $HitStarts[$i] - 1;
		$posQue = $QueryStarts[$i] - 1;

		for($j = 1; $j<=length($HitStrings[$i]); $j++){
			$hitChar = substr($HitStrings[$i],$j-1,1);
			$posHit++ if ($hitChar ne "-");
			$queChar = substr($QueryStrings[$i],$j-1,1);
			$posQue++ if ($queChar ne ".");

			$HitCharOfPos{$posQue} 	= $hitChar 	if (($hitChar ne "-")and ( $queChar ne "." )) ;
			$HitPosOfPos{$posQue} 	= $posHit 	if (($hitChar ne "-")and ( $queChar ne "." )) ;
		}; #for j
	}; #for i

#find list of matched hit sites: NOTE: same myHitID, same QueryName!
	foreach $hmmSite (@HMMSites){
		$hitSite = checkHitSiteForThis($hmmSite);
		next if ($hitSite eq "");
		(undef,$ecCnt,$otherCnt) = split(/\s+/,$hmmSite);
		$ratio = $ecCnt / ($ecCnt + $otherCnt);
		$ratio = sprintf("%.3f",$ratio);
		print OUTSITE $myHitID ."\t". $queryName ."\t". $hitSite. "\t". $ecCnt."\t".$otherCnt ."\t". $ratio."\n";
	};
}; # sub 


sub checkHitSiteForThis{	#BD:168:T|253:T|277:G|	18	30
	my $type = shift;
	($type, $ECCnt, undef) = split(/\s+/,$type);
	return "" if ($type =~/NONE/);
	return "" if ($ECCnt < 1);
	
	my $RES = substr($type,0,3);
	$type 	= substr($type,3);
	my @PosAA = split(/\|/,$type); 
	foreach(@PosAA){
		$RES = $RES . $_; 
		my ($pos,$aa) = split(/:/,$_);		
		my $matched = "m";
		$matched = "n" if ( (!exists $HitCharOfPos{$pos}) or ($HitCharOfPos{$pos} ne $aa) );
		$matchedPos = "0";
		$matchedPos = $HitPosOfPos{$pos} if (exists $HitCharOfPos{$pos});
		$RES = $RES.":$matched:$matchedPos|";
		return "" if ($RES =~/:n/);
	};
	return "" if ($RES =~/:n/);
	return $RES;
};


sub readSiteFile{
	my $myHmmName = shift;
	my $hmmSiteFile = "$HMMDir/$myHmmName.hmm.sites";
#	print "hmm sites file is $hmmSiteFile\n";
	if (! -e $hmmSiteFile){
		#warn "no [$hmmSiteFile] file\n";
		exit;
	};
	open(SITE,$hmmSiteFile) || warn "no [$hmmSiteFile]\n";
	while(<SITE>){
		chomp;
		push(@HMMSites,$_);
	};
	close(SITE);
};

