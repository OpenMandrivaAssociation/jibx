# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define gcj_support 0

%define section free

Name:           jibx
Version:        1.2.2
Release:        %mkrel 1
Epoch:          0
Summary:        Framework for binding XML data to Java objects
License:        Public Domain
Url:            http://jibx.sourceforge.net/
Group:          Development/Java
#Vendor: %{?_vendorinfo:%{_vendorinfo}}%{!?_vendorinfo:%{_vendor}}
#Distribution: %{?_distribution:%{_distribution}}%{!?_distribution:%{_vendor}}
Source0:        %{name}_1_1_6.zip
Source1:        jibx-bind-1.1.5.pom
Source2:        jibx-extras-1.1.5.pom
Source3:        jibx-run-1.1.5.pom

BuildRequires:  java-rpmbuild >= 0:1.7.2
BuildRequires:  ant
BuildRequires:  ant-junit
BuildRequires:  junit
BuildRequires:  asm2 >= 0:2.1
BuildRequires:  bcel
BuildRequires:  bea-stax-api
BuildRequires:  qdox
BuildRequires:  wstx
BuildRequires:  dom4j
BuildRequires:  jdom
BuildRequires:  xmlpull-api >= 0:1.1.4
BuildRequires:  xpp3
BuildRequires:  log4j
%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
%endif

Requires:       asm2 >= 0:2.1
Requires:       bcel
Requires:       bea-stax-api
Requires:       qdox
Requires:       wstx
Requires:       dom4j
Requires:       jdom
Requires:       xmlpull-api >= 0:1.1.4
Requires:       xpp3
Requires:       log4j
Requires(post):    jpackage-utils >= 0:1.7.2
Requires(postun):  jpackage-utils >= 0:1.7.2

%if ! %{gcj_support}
BuildArch:      noarch
%endif

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
JiBX is a framework for binding XML data to Java objects. It lets you
work with data from XML documents using your own class structures.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
%{summary}.

%prep
%setup -q -n %{name}
%{__perl} -pi -e 's/<attribute name="Class-Path".*\n//g' build/build.xml
%remove_java_binaries

%build

# dom4j and jdom are optional. If povided, jibx-extras is built with
# support for those models

build-jar-repository -p lib \
asm2/asm2 \
asm2/asm2-commons \
bcel \
bea-stax-api \
dom4j \
jdom \
log4j \
qdox \
wstx/wstx-asl \
xmlpull-api \
xpp3

pushd build/
sed -i -e s:stax-api.jar:bea-stax-api.jar:g build.xml
sed -i -e s:wstx-asl.jar:wstx-asl.jar:g build.xml
export OPT_JAR_LIST="`%{__cat} %{_sysconfdir}/ant.d/junit`"
export CLASSPATH=$(build-classpath junit)
%{ant} current devdoc #testing

%install
rm -rf $RPM_BUILD_ROOT

install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/%{name}
for sub_component in bind extras run; do
install -m 644 lib/jibx-${sub_component}.jar \
     $RPM_BUILD_ROOT%{_javadir}/%{name}/${sub_component}-%{version}.jar
done

%add_to_maven_depmap org.jibx %{name}-bind %{version} JPP/%{name} bind
%add_to_maven_depmap jibx %{name}-bind %{version} JPP/%{name} bind
%add_to_maven_depmap org.jibx %{name}-extras %{version} JPP/%{name} extras
%add_to_maven_depmap jibx %{name}-extras %{version} JPP/%{name} extras
%add_to_maven_depmap org.jibx %{name}-run %{version} JPP/%{name} run
%add_to_maven_depmap jibx %{name}-run %{version} JPP/%{name} run

# create unprefixed and unversioned symlinks
(cd $RPM_BUILD_ROOT%{_javadir}/%{name}
for jar in *-%{version}*; do ln -sf ${jar} ${jar/-%{version}/}; done
)

# poms
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -pm 644 %{SOURCE1} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}-bind.pom
install -pm 644 %{SOURCE2} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}-extras.pom
install -pm 644 %{SOURCE3} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}-extras.pom


install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr build/docs/dev/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}/
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}

%{gcj_compile}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_maven_depmap
%if %{gcj_support}
%{update_gcjdb}
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%dir %{_javadir}/%{name}
%{_javadir}/%{name}/*.jar
%{_datadir}/maven2/poms/*
%config(noreplace) %{_mavendepmapfragdir}/jibx
%{gcj_files}

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}
