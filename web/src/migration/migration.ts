// <!-- <button id="migrate-id" type="submit" class="btn btn-danger w-100">Migrate</button> -->

// async function migrate(button: HTMLInputElement) {
//   const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
//   const urlParams = new URLSearchParams(window.location.search);
//   const token = urlParams.get('token') || '';

//   button.disabled = true;

//   if (token) {
//     const client = new HttpClient(token);

//     try {
//       let job = await client.post<ApiJobDetails>(`${apiUrl}/bookmark/migrate`);

//       console.log('job', job);

//       if (job?.status) {
//         while (job.status !== 'complete') {
//           await wait(2000);

//           job = await client.get<ApiJobDetails>(
//             `${apiUrl}/bookmark/job/status/${job.jobId}`
//           );

//           console.log('\tjob:check', job);
//         }
//       }

//       if (!job.info?.success) {
//         alert('The migration process finished unsuccessfully.');
//       }
//     } catch (error) {
//       console.log('ERROR', error);
//     }
//   }

//   button.disabled = false;
// }

// document
//   .getElementById('migrate-id')
//   ?.addEventListener('click', (e) => migrate(e.target as HTMLInputElement));
