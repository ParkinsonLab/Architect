#! /usr/bin/perl -w

#Search a hmm profile against a fasta file

$MAX_EVALUE = 0.02;

#===INPUT===#
$HMMFile	=	$ARGV[0];
$FastaFile 	= 	$ARGV[1];
$hmmsearch 	= 	"../../progs/hmmsearch";

#===OUTPUT===#
$OutFile 	=	$ARGV[2];
$tmpfile = "$OutFile.raw";

#=================================================
# call hmmsearch program
system("$hmmsearch -E $MAX_EVALUE --cpu 8 $HMMFile $FastaFile > $tmpfile");	

#=================================================
#processing result file:
open(FILE,"$tmpfile") || die;

%InfoOfId = ();
@IDs = ();
$lcnt = 0;
$readSummary = 1;
$myID = "any ID would work";
$matchedFlag = 0;
while($line = <FILE>){
	$lcnt++;
#	print $line;
	next if ($line =~ /^\s+$/);	# blank
	next if ($lcnt <17);	# result starts at line 16	

	if ($line =~ /------ inclusion threshold ------/){
		$readSummary = 0;
		next;
	};

	if ($line =~ /Domain annotation for each sequence/){
		$readSummary = 0;
		next;
	}
	if ($line =~ /No hits detected that satisfy reporting thresholds/){
		$readSummary = 0;
		next;
	}
	# start read summary:
	if ($readSummary == 1){
		(undef, $fullEval, $fullBs, undef, $bestEval, $bestBS, undef, undef, $num_dom, $spACID) = split(/\s+/,$line);
		next if (!$spACID);	
		push(@IDs,$spACID);
		$InfoOfId {$spACID} = $spACID ."\t". $fullEval ."\t". $fullBs ."\t". $num_dom ."\t". $bestEval ."\t". $bestBS; 
	}
	else{	# Read annotation info:

#>> sp|Q2IL01|NUOI1_ANADE  239 290397 PF00037| 1.6.99.5|
#   #    score  bias  c-Evalue  i-Evalue hmmfrom  hmm to    alifrom  ali to    envfrom  env to     acc
# ---   ------ ----- --------- --------- ------- -------    ------- -------    ------- -------    ----
#   1 !  247.7   0.1   4.1e-75     2e-72       4     198 ..       8     232 ..       5     234 .. 0.96
		if ($line =~ /^>>/){
			(undef, $myID) = split(/\s+/,$line);
			
			next;
		}
		if ($line =~ /\!|\?/){
			@Tokens = split(/\s+/,$line);
			$bscore  = $Tokens[3];
			$cEval	 = $Tokens[5];
			$hmmfrom = $Tokens[7];
			$hmmto	 = $Tokens[8];
			$alifrom = $Tokens[10];
			$alito	 = $Tokens[11];
			$InfoOfId {$myID} = $InfoOfId {$myID} ."\t". $cEval ."\t". $bscore ."\t". $hmmfrom ."\t". $hmmto ."\t". $alifrom ."\t". $alito if (exists $InfoOfId {$myID});
			$matchedFlag = 1;
		};
	
	}	# Read annotation info
}
close(FILE);

#adding  ">>" symbols to the end of file:
#open(FILE,">xxx");
#print FILE ">> \n";
#close(FILE);
#system("cat xxx >> $tmpfile");
open(FILE,">>",$tmpfile);
print FILE ">> \n";
close(FILE);

### Print output:
#header with ">" at the begining
open(OUT,">",$OutFile) || die;
print OUT ">HMMSEARCH RESULT: $hmmsearch -E $MAX_EVALUE $HMMFile $FastaFile > $OutFile\n";
print OUT ">format: spACID	<tab>	full-e-value	<tab>	full-bitscore	<tab>	number-of-domains	<tab> best-e-value	<tab>	best-bitscore	<tab>	first-eval <tab> first-bscore	<tab>	hmmfrom	<tab>	hmmto	<tab> align-from	<tab>	align-to	<tab>	the same format for next domains, if any\n";

#hit results:
foreach $id (@IDs){
	print OUT $InfoOfId {$id}."\n";
}
close(OUT);




