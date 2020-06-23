# Osparc opencor
[![master.dev](https://img.shields.io/website?down_message=offline&label=master.dev&up_message=run&url=https%3A//osparc01.speag.com)](https://osparc01.speag.com/study/194bb264-a717-11e9-9dff-02420aff2767)
[![staging](https://img.shields.io/website?down_message=offline&label=staging&up_message=run&url=https%3A//staging.osparc.io)](https://staging.osparc.io/study/194bb264-a717-11e9-9dff-02420aff2767)
[![osparc.io](https://img.shields.io/website?down_message=offline&label=osparc.io&up_message=run&url=https%3A//osparc.io)](https://osparc.io/study/194bb264-a717-11e9-9dff-02420aff2767)

![Project Thumbnail](https://user-images.githubusercontent.com/33152403/61133437-be4cf700-a4bd-11e9-8b2a-c6425e15abea.png)

We are using the Fabbri et al (2017) sinoatrial cell model: https://models.physiomeproject.org/e/568

The model includes autonomic modulation via inclusion of the effects of ACh on If, ICaL, SR calcium uptake, and IK,ACh, and the effect of isoprenaline on If, ICaL, INaK, maximal Ca uptake, and IKs. We are varying the concentration of ACh according to the stimulation level, while isoprenaline is encoded to be "on" or "off" only (we use the "on" version in this exemplar). The range of ACh we're allowing is beyond what has been presented in the paper.
