FROM parkinsonlab/architect:latest

COPY cplex cplex

RUN cd cplex \
&& cplex_installer=cplex_installer.bin \
&& cplex_installer_properties=cplex.installer.properties \
&& if [ -f $cplex_installer ] ; then \
	chmod a+rwx $cplex_installer \
	&& ./$cplex_installer -f ${cplex_installer_properties} \
	&& for not_needed in 'Uninstall' 'concert' 'cpoptimizer' 'doc' 'opl'; \
		do rm -rf $not_needed; \
	done \
	&& rm $cplex_installer \
	&& rm $cplex_installer_properties \
	&& cd python \ 
	&& python3.7 setup.py install; \
fi

RUN git clone https://github.com/ParkinsonLab/Architect

RUN cd Architect \
&& wget http://compsysbio.org/projects/Architect/Database.tar.gz \
&& tar -xzvf Database.tar.gz \
&& rm -rf Database.tar.gz

RUN mkdir /indiv_tools

RUN mkdir /architect_run