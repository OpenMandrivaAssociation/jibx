%{?_javapackages_macros:%_javapackages_macros}
%global debug_package %{nil}

Name:          jibx
Version:       1.2.5
Release:       9.2
Summary:       Framework for binding XML data to Java objects
Group:		Development/Java
License:       BSD and ASL 1.1
URL:           http://sourceforge.net/projects/jibx/
Source0:       http://sourceforge.net/projects/jibx/files/jibx/jibx-1.2.5/%{name}_1_2_5.zip
Patch0:        %{name}-classpath.patch
Patch1:        %{name}-%{version}-poms.patch
Patch2:		jibx-1.2.5-qdox2.patch

BuildRequires: java-devel >= 1:1.6.0
BuildRequires: ant
BuildRequires: ant-junit
BuildRequires: junit
BuildRequires: objectweb-asm3
BuildRequires: bcel
BuildRequires: bea-stax-api
BuildRequires: eclipse-equinox-osgi
BuildRequires: eclipse-jdt
BuildRequires: eclipse-platform
BuildRequires: joda-time
BuildRequires: qdox
BuildRequires: dom4j
BuildRequires: jdom
BuildRequires: xpp3
BuildRequires: log4j12

Requires:      java
Requires:      jpackage-utils

%description
JiBX is a framework for binding XML data to Java objects. It lets you
work with data from XML documents using your own class structures. 

%package javadoc
Summary:       Javadoc for %{name}

%description javadoc
This package contains the API documentation for %{name}.


%prep
%setup -q -n %{name}
#Patch to add the bundled jar dependencies in the classpath
%patch0 -p1
#Patch to add maven poms
%patch1 -p0
%patch2 -p1

find -name '*.class' -delete
find -name '*.jar' -delete

rm -rf %{_builddir}/%{name}/build/docs/src/*


#Symlink the eclipse dependencies
# platform
plugin_file=`ls %{_libdir}/eclipse/plugins/org.eclipse.core.contenttype_*.jar`
ln -s "$plugin_file" lib/org.eclipse.core.contenttype.jar

plugin_file=`ls %{_libdir}/eclipse/plugins/org.eclipse.core.jobs_*.jar`
ln -s "$plugin_file" lib/org.eclipse.core.jobs.jar

plugin_file=`ls %{_libdir}/eclipse/plugins/org.eclipse.core.runtime_*.jar`
ln -s "$plugin_file" lib/org.eclipse.core.runtime.jar

plugin_file=`ls %{_libdir}/eclipse/plugins/org.eclipse.core.resources_*.jar`
ln -s "$plugin_file" lib/org.eclipse.core.resources.jar

plugin_file=`ls %{_libdir}/eclipse/plugins/org.eclipse.equinox.common_*.jar`
ln -s "$plugin_file" lib/org.eclipse.equinox.common.jar

plugin_file=`ls %{_libdir}/eclipse/plugins/org.eclipse.equinox.preferences_*.jar`
ln -s "$plugin_file" lib/org.eclipse.equinox.preferences.jar

plugin_file=`ls %{_libdir}/eclipse/plugins/org.eclipse.text_*.jar`
ln -s "$plugin_file" lib/org.eclipse.text.jar

# new location in eclipse 4.4.0-0.29.git201406042000
plugin_file=`ls %{_libdir}/eclipse/dropins/jdt/plugins/org.eclipse.jdt.core_*jar`
ln -s "$plugin_file" lib/org.eclipse.jdt.core.jar

# equinox-osgi
#plugin_file=`ls %%{_libdir}/eclipse/plugins/org.eclipse.osgi_*.jar`
#ln -s "$plugin_file" lib/org.eclipse.osgi.jar
ln -s $(build-classpath eclipse/osgi) lib/org.eclipse.osgi.jar

# jdt
plugin_file=`ls %{_libdir}/eclipse/dropins/jdt/plugins/org.eclipse.jdt.core.manipulation_*.jar`
ln -s "$plugin_file" lib/org.eclipse.jdt.core.manipulation.jar


build-jar-repository -p lib \
bcel \
bea-stax-api \
dom4j \
jdom \
joda-time \
qdox \
xpp3 

ln -s $(build-classpath objectweb-asm3/asm) lib/
ln -s $(build-classpath objectweb-asm3/asm-commons) lib/
ln -s $(build-classpath log4j12-1.2.17) lib/

sed -i '/Class-Path/I d' %{_builddir}/%{name}/build/build.xml


%build
pushd build/
sed -i -e s:stax-api.jar:bea-stax-api.jar:g build.xml

# thanks to msrb@redhat.com
sed -i 's|version}" arg2="1.5"|version}" arg2="1.8"|g' build.xml
javac jenable/JEnable.java

export CLASSPATH=$(build-classpath junit)
ant current -Dant.build.javac.source=1.5 -Dant.build.javac.target=1.5 #test-multiples test-singles test-extras basic-blackbox blackbox devdoc javadoc

%install
install -d -m 755 %{buildroot}/%{_javadir}/%{name}
install -d -m 755 %{buildroot}%{_mavenpomdir}

install -pm 644 build/maven/pom.xml %{buildroot}%{_mavenpomdir}/JPP.%{name}-main-reactor.pom
%add_maven_depmap JPP.%{name}-main-reactor.pom

for sub_component in bind extras run schema tools; do
install -m 644 lib/%{name}-${sub_component}.jar \
%{buildroot}/%{_javadir}/%{name}/${sub_component}.jar
install -pm 644 build/maven/jibx-${sub_component}/pom.xml %{buildroot}%{_mavenpomdir}/JPP.%{name}-${sub_component}.pom
%add_maven_depmap JPP.%{name}-${sub_component}.pom %{name}/${sub_component}.jar
done

mkdir -p %{buildroot}/%{_javadocdir}/%{name}
cp -rp %{_builddir}/%{name}/build/docs/* \
%{buildroot}/%{_javadocdir}/%{name}/


%files -f .mfiles

%files javadoc
%{_javadocdir}/%{name}

%changelog
* Sun Aug 25 2013 gil cattaneo <puntogil@libero.it> 1.2.5-5
- install unversioned jars
- preserve poms timestamp

* Sat Aug 24 2013 gil cattaneo <puntogil@libero.it> 1.2.5-4
- fix rhbz#992870
- removed asm2 references
- fix some rpmlint problems
- fix BR list

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sat Mar 23 2013 Johannes Lips <hannes@fedoraproject.org> - 1.2.5-2
- added ant build option to fix #845625

* Wed Feb 27 2013 Johannes Lips <hannes@fedoraproject.org> - 1.2.5-1
- update to latest upstream version

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.4-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 25 2012 Johannes Lips <hannes@fedoraproject.org> - 1.2.4-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild 

* Sat Jul 21 2012 Johannes Lips <hannes@fedoraproject.org> - 1.2.4-5
- fixed the empty debuginfo package

* Tue Jul 17 2012 Patryk Obara <pobara@redhat.com> - 1.2.4-4
- fixed the maven pom patch (#840929)

* Tue May 29 2012 Johannes Lips <hannes@fedoraproject.org> - 1.2.4-3
- add maven pom (patch from Gil Cattaneo #825465)
- minor changes to adapt to guideline changes

* Sun May 20 2012 Johannes Lips <johannes.lips@googlemail.com> - 1.2.4-2
- removed the empty debuginfo subpackage caused by the removal of noarch
 
* Sat May 05 2012 Johannes Lips <johannes.lips@googlemail.com> - 1.2.4-1
- update to recent upstream version 
- removed buildarch noarch

* Sat Jan 14 2012 Johannes Lips <johannes.lips@googlemail.com> - 1.2.3-3
- added eclipse-platform as BR
- fixed the jdt.core path 

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Apr 21 2011 Johannes Lips <johannes.lips@googlemail.com> - 1.2.3-1
- Update to 1.2.3

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.2-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Sep 09 2010 Johannes Lips <johannes.lips@googlemail.com> - 1.2.2-7
- added a version requirement for java-devel
- disabled the tests

* Thu Sep 09 2010 Johannes Lips <johannes.lips@googlemail.com> - 1.2.2-6
- added a patch to meet all the dependencies

* Sun Sep 05 2010 Johannes Lips <johannes.lips@googlemail.com> - 1.2.2-5
- removed the classpath
- changed the license
- removed most required packages

* Thu Sep 02 2010 Johannes Lips <johannes.lips@googlemail.com> - 1.2.2-4
- changed the structure
- 
* Thu Sep 02 2010 Johannes Lips <johannes.lips@googlemail.com> - 1.2.2-3
- symlinked all eclipse plugins
- removed all bundled dependencies
- added the build-jar-repository in the %%prep section
- added the tests

* Fri Aug 27 2010 Johannes Lips <johannes.lips@googlemail.com> - 1.2.2-2
- consistent usage of %%{buildroot}
- added missing javadoc file attributes

* Fri Aug 27 2010 Johannes Lips <johannes.lips@googlemail.com> - 1.2.2-1
- initial build
